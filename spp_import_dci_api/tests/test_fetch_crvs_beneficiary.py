from datetime import datetime, timezone

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

from ..models import constants


class TestCrvsBeneficiary(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.location_type = cls.env["spp.crvs.location.type"].create(
            {
                "name": "Test Location Type",
                "location_type": "test_location_type",
            }
        )

        cls.parent_location_id = cls.env["spp.crvs.location"].create(
            {
                "location_name": "Test Parent Location",
                "identifier": "test_parent_location",
                "location_type": cls.location_type.id,
                "identifier_name": "test_parent_location",
            }
        )
        cls.location_id = cls.env["spp.crvs.location"].create(
            {
                "location_name": "Test Location",
                "identifier": "test_location",
                "location_type": cls.location_type.id,
                "parent_id": cls.parent_location_id.id,
                "identifier_name": "test_location",
            }
        )
        cls.child_location_id = cls.env["spp.crvs.location"].create(
            {
                "location_name": "Test Child Location",
                "identifier": "test_child_location",
                "location_type": cls.location_type.id,
                "parent_id": cls.location_id.id,
                "identifier_name": "test_child_location",
            }
        )

    def test_compute_name(self):
        self.parent_location_id._compute_name()
        self.assertEqual(self.parent_location_id.name, "Test Parent Location")

        self.location_id._compute_name()
        self.assertEqual(self.location_id.name, "Test Parent Location - Test Location")

        self.child_location_id._compute_name()
        self.assertEqual(self.child_location_id.name, "Test Parent Location - Test Location - Test Child Location")

    def test_get_or_set_location_hashmap(self):
        hashmap = {}
        self.env["spp.crvs.location"].get_or_set_location_hashmap("test location type", hashmap)

        self.assertEqual(len(hashmap), 1)
        self.assertEqual(hashmap["test location type"].location_type, "test location type")

    def test_get_crvs_location_vals(self):
        additional_type_id = self.env["spp.crvs.location"].get_or_set_location_hashmap("test location type", {})

        identifer = {
            "name": "Test Location",
            "identifier": "test_location",
        }

        location = {
            "@type": "Location",
            "name": "Test Location",
            "containedInPlace": "test_parent_location",
        }

        location_vals = self.env["spp.crvs.location"].get_crvs_location_vals(identifer, location, additional_type_id)

        self.assertEqual(location_vals["identifier_name"], "Test Location")
        self.assertEqual(location_vals["identifier"], "test_location")
        self.assertEqual(location_vals["location_type"], "Location")
        self.assertEqual(location_vals["location_additional_type_id"], additional_type_id.id)
        self.assertEqual(location_vals["location_name"], "Test Location")
        self.assertTrue(bool(location_vals["parent_id"]))

    def test_update_or_create_location(self):
        identifer = {
            "identifier": "test_parent_location",
        }
        existing_vals = {
            "location_name": "Test_Parent_Location",
            "identifier": "test_parent_location",
        }
        self.env["spp.crvs.location"].update_or_create_location(identifer, existing_vals)
        self.assertEqual(self.parent_location_id.location_name, "Test_Parent_Location")

        new_vals = {
            "location_name": "Test New Location",
            "identifier": "test_new_location",
            "location_type": self.location_type.id,
            "parent_id": self.parent_location_id.id,
            "identifier_name": "test_new_location",
        }
        new_identifer = {
            "identifier": "test_new_location",
        }
        self.env["spp.crvs.location"].update_or_create_location(new_identifer, new_vals)
        self.assertTrue(self.env["spp.crvs.location"].search([("identifier", "=", "test_new_location")]))

    def test_process_location(self):
        result = {
            "locations": [
                {
                    "additionalType": "Test Location",
                    "identifier": [
                        {
                            "location_name": "Test Location",
                            "identifier": "test_parent_location",
                            "identifier_name": "test_parent_location",
                        }
                    ],
                }
            ]
        }

        self.env["spp.crvs.location"].process_location(result)
        self.assertTrue(self.env["spp.crvs.location"].search([]))

    def test_get_parent(self):
        parent = self.parent_location_id.get_parent()
        self.assertEqual(parent, self.parent_location_id)

        parent = self.location_id.get_parent()
        self.assertEqual(parent, self.location_id)

        parent = self.child_location_id.get_parent()
        self.assertEqual(parent, self.location_id)


class TestFetchCRVSBeneficiary(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.location_type_id = cls.env["spp.crvs.location.type"].create(
            {
                "name": "Test Location Type",
                "location_type": "test_location_type",
            }
        )

        cls.fetch_crvs_beneficiary_id = cls.env["spp.fetch.crvs.beneficiary"].create(
            {
                "data_source_id": cls.env.ref("spp_import_dci_api.spp_crvs_data_source").id,
                "name": "Test Fetch CRVS Beneficiary",
                "location_type_id": cls.location_type_id.id,
            }
        )

    def test_compute_location_id_domain(self):
        self.fetch_crvs_beneficiary_id._compute_location_id_domain()
        self.assertEqual(
            self.fetch_crvs_beneficiary_id.location_id_domain,
            f'[["location_additional_type_id", "=", {self.location_type_id.id}]]',
        )

    def test_get_data_source_paths(self):
        paths = self.fetch_crvs_beneficiary_id.get_data_source_paths()

        self.assertEqual(
            paths,
            {
                "Registry Sync Search": "/registry/sync/search",
                "Authentication": "/oauth2/client/token",
                "Location": "/.well-known/locations.json",
            },
        )

        path = self.env["spp.data.source.path"].search([("key", "=", constants.DATA_SOURCE_SEARCH_PATH_NAME)], limit=1)
        path.write({"key": "new Key"})

        with self.assertRaises(ValidationError):
            self.fetch_crvs_beneficiary_id.get_data_source_paths()

    def test_get_crvs_search_url(self):
        paths = self.fetch_crvs_beneficiary_id.get_data_source_paths()
        search_url = self.fetch_crvs_beneficiary_id.get_crvs_search_url(paths)

        self.assertEqual(search_url, "https://dci.opencrvs.lab.cdpi.dev/registry/sync/search")

    def test_get_crvs_auth_url(self):
        paths = self.fetch_crvs_beneficiary_id.get_data_source_paths()
        auth_url = self.fetch_crvs_beneficiary_id.get_crvs_auth_url(paths)

        grant_type = self.env["ir.config_parameter"].sudo().get_param("crvs_grant_type")
        client_id = self.env["ir.config_parameter"].sudo().get_param("crvs_client_id")
        client_secret = self.env["ir.config_parameter"].sudo().get_param("crvs_client_secret")
        self.assertEqual(
            auth_url,
            f"{self.fetch_crvs_beneficiary_id.data_source_id.url}/oauth2/client/token?grant_type={grant_type}&client_id={client_id}&client_secret={client_secret}",
        )

    def test_get_headers_for_request(self):
        self.assertEqual(self.fetch_crvs_beneficiary_id.get_headers_for_request(), {"Content-Type": "application/json"})

    def test_get_header_for_body(self):
        today_isoformat = datetime.now(timezone.utc).isoformat()
        version = 1
        message_id = "test_id_123"
        header_for_body = self.fetch_crvs_beneficiary_id.get_header_for_body(version, today_isoformat, message_id)

        sender_id = self.env["ir.config_parameter"].sudo().get_param("web.base.url") or ""

        self.assertEqual(
            header_for_body,
            {
                "version": version,
                "message_id": message_id,
                "message_ts": today_isoformat,
                "action": "search",
                "sender_id": sender_id,
                "sender_uri": "",
                "receiver_id": "crvs",
                "total_count": 10,
                "encryption_algorithm": "",
            },
        )

    def test_get_query(self):
        query = self.fetch_crvs_beneficiary_id.get_query()

        self.assertEqual(
            query,
            [
                {
                    "expression1": {
                        "attribute_name": "birthdate",
                        "operator": "gt",
                        "attribute_value": "2023-11-15",
                    },
                    "condition": "and",
                    "expression2": {
                        "attribute_name": "birthdate",
                        "operator": "lt",
                        "attribute_value": "2023-11-15",
                    },
                }
            ],
        )

    def test_get_search_request(self):
        today_isoformat = datetime.now(timezone.utc).isoformat()
        reference_id = "test_reference_id"
        search_request = self.fetch_crvs_beneficiary_id.get_search_request(reference_id, today_isoformat)

        self.assertEqual(
            search_request,
            {
                "reference_id": reference_id,
                "timestamp": today_isoformat,
                "search_criteria": {
                    "reg_type": "ocrvs:registry_type:birth",
                    "query_type": "predicate",
                    "query": [
                        {
                            "expression1": {
                                "attribute_name": "birthdate",
                                "operator": "gt",
                                "attribute_value": "2023-11-15",
                            },
                            "condition": "and",
                            "expression2": {
                                "attribute_name": "birthdate",
                                "operator": "lt",
                                "attribute_value": "2023-11-15",
                            },
                        }
                    ],
                },
            },
        )

    def test_get_message(self):
        today_isoformat = datetime.now(timezone.utc).isoformat()
        transaction_id = "test_transaction_id"
        reference_id = "test_reference_id"

        message = self.fetch_crvs_beneficiary_id.get_message(today_isoformat, transaction_id, reference_id)

        self.assertEqual(message["transaction_id"], transaction_id)
        self.assertEqual(message["search_request"][0]["reference_id"], reference_id)
        self.assertEqual(message["search_request"][0]["timestamp"], today_isoformat)

    def test_get_data(self):
        data = self.fetch_crvs_beneficiary_id.get_data("", "Authorization: Bearer test_token", "test_url")
        self.assertEqual(
            data,
            {
                "header": "Authorization: Bearer test_token",
                "message": "test_url",
            },
        )
