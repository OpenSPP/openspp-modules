from datetime import datetime
from unittest.mock import Mock, patch

from odoo import _
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestRegistrant(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._test_individual = cls.env["res.partner"].create(
            {
                "name": "Jon Snow",
                "given_name": "Jon",
                "family_name": "Targaryen",
                "birth_place": "Tower of Joy",
                "is_registrant": True,
                "is_group": False,
            }
        )
        cls._test_household = cls.env["res.partner"].create(
            {
                "name": "Winterfell",
                "group_membership_ids": [
                    (
                        0,
                        0,
                        {
                            "individual": cls._test_individual.id,
                            "kind": [
                                (
                                    4,
                                    cls.env.ref("g2p_registry_membership.group_membership_kind_head").id,
                                )
                            ],
                        },
                    )
                ],
            }
        )

    def _create_test_id_pass(self):
        self._test_id_pass = self.env["spp.id.pass"].create(
            {
                "name": "Keycloak [Local]",
                "api_url": "http://localhost:8080/",
                "api_username": "admin",
                "api_password": "admin",
                "auth_token_url": "http://localhost:8080/auth/realms/master/protocol/openid-connect/token",
                "expiry_length": 1,
                "expiry_length_type": "years",
                "is_active": True,
                "filename_prefix": "kclk",
            }
        )

    def _create_test_id_queue(self):
        if not self.env.get("spp.print.queue.id"):
            raise ValidationError(_("Object `OpenSPPIDQueue` not yet existed!"))
        self._test_id_queue = self.env["spp.print.queue.id"].create(
            {
                "registrant_id": self._test_household.id,
                "requested_by": self.env.user.id,
                "id_type": self.env.ref("spp_idpass.id_type_idpass").id,
            }
        )

    def _create_test_reg_id(self):
        return self.env["g2p.reg.id"].create(
            {
                "partner_id": self._test_individual.id,
                "id_type": self.env.ref("spp_idpass.id_type_idpass").id,
            }
        )

    def test_01_check_existing_id_existed(self):
        test_reg = self._create_test_reg_id()
        self._test_individual.check_existing_id("1234567890")
        self.assertEqual(test_reg.value, "1234567890", "Value should be data to check!")

    def test_02_check_existing_id_not_existed(self):
        self._test_individual.check_existing_id("1234567890")
        self.assertEqual(
            self._test_individual.reg_ids[0].value,
            "1234567890",
            "Value should be data to check!",
        )

    def test_03_send_idpass_parameters_false_vals(self):
        vals = {
            "idpass": 1_000_0000,
            "id_queue": 200_000,
        }
        with self.assertRaises(ValidationError):
            self._test_individual.send_idpass_parameters(vals)

    @patch("requests.post")
    def test_04_send_idpass_parameters_correct_vals_response_403(self, mock_post):
        mock_post.return_value = Mock(status_code=403, json=lambda: {"reason": "Not allowed mock post!"})
        self._create_test_id_pass()
        vals = {"idpass": self._test_id_pass.id}
        with self.assertRaises(ValidationError):
            self._test_individual.send_idpass_parameters(vals)

    @patch("requests.post")
    def test_05_send_idpass_parameters_correct_vals_response_200(self, mock_post):
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {"files": {"pdf": "1234567890123456789012345678TEST"}},
        )
        self._create_test_id_pass()
        self._create_test_reg_id()
        try:
            self._create_test_id_queue()
        except ValidationError as e:
            self.skipTest(e.args)
        vals = {"idpass": self._test_id_pass.id, "id_queue": self._test_id_queue.id}
        self._test_household.send_idpass_parameters(vals)
        self.assertEqual(
            self._test_id_queue.id_pdf,
            "TEST",
            "Id Queue should have correct Id PDF!",
        )
        jon_snow_identification_number = f"{self._test_individual.id:09d}"
        today_strf = datetime.today().strftime("%Y-%m-%d")
        self.assertEqual(
            self._test_id_queue.id_pdf_filename,
            f"kclk_{jon_snow_identification_number}_{today_strf}.pdf",
            "Id Queue should have correct PDF file name!",
        )
