import json
import logging
import uuid
from datetime import datetime, timezone
from urllib.parse import urlencode

import requests
from dateutil import parser

from odoo import _, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import safe_eval

from ..models import constants

_logger = logging.getLogger(__name__)

DATA_SOURCE_NAME = "CRVS"
DATA_SOURCE_SEARCH_PATH_NAME = "Registry Sync Search"
DATA_SOURCE_AUTH_PATH_NAME = "Authentication"
DATA_SOURCE_LOCATION_PATH_NAME = "Location"

DEFAULT_YEAR = 2023
DEFAULT_MONTH = 11
DEFAULT_DAY = 15


class FetchDomainFilter(models.TransientModel):
    _name = "spp.fetch.domain.filter"
    _description = "Fetch Domain Filter"

    def _get_location_selection(self):
        location_selection = [("", "All locations")]

        data_source_id = self.env["spp.data.source"].search(
            [("name", "=", DATA_SOURCE_NAME)], limit=1
        )

        if data_source_id:
            location_path = ""
            data_source_path_id = self.env["spp.data.source.path"].search(
                [
                    ("name", "=", DATA_SOURCE_LOCATION_PATH_NAME),
                    ("data_source_id", "=", data_source_id.id),
                ],
                limit=1,
            )
            if data_source_path_id:
                location_path = data_source_path_id.path

            if location_path:
                url = f"{data_source_id.url}{location_path}"
                response = requests.get(url)

                if response.ok:
                    result = response.json()
                    locations = result.get("locations", [])
                    for loc in locations:
                        name = loc.get("name", "")
                        if name:
                            identifiers = loc.get("identifier", [])

                            for identifier in identifiers:
                                if identifier.get("identifier"):
                                    location_selection.append(
                                        (identifier["identifier"], name)
                                    )

        return location_selection

    birthdate = fields.Date("Birth Date")
    location = fields.Selection(_get_location_selection)


class SPPFetchCRVSBeneficiary(models.Model):
    _name = "spp.fetch.crvs.beneficiary"
    _description = "Fetch CRVS Beneficiary"

    def _get_default_domain(self):
        return (
            f'["&",["birthdate",">","{DEFAULT_YEAR}-{DEFAULT_MONTH}-{DEFAULT_DAY}"]'
            f',["birthdate","<","{DEFAULT_YEAR}-{DEFAULT_MONTH}-{DEFAULT_DAY}"],'
            ' ["location","=",""]]'
        )

    data_source_id = fields.Many2one(
        "spp.data.source",
        required=True,
        default=lambda self: self.env["spp.data.source"].search(
            [("name", "=", DATA_SOURCE_NAME)], limit=1
        ),
        readonly=True,
    )

    name = fields.Char("Search Criteria Name", required=True)

    domain = fields.Text(
        default=_get_default_domain,
        required=True,
    )

    done_imported = fields.Boolean()
    imported_individual_ids = fields.One2many(
        "spp.crvs.imported.individuals",
        "fetch_crvs_id",
        "Imported Individuals",
        readonly=True,
    )

    TIMEOUT = 10

    def get_data_source_paths(self):
        self.ensure_one()

        paths = {}

        for path_id in self.data_source_id.data_source_path_ids:
            paths[path_id.name] = path_id.path

        if DATA_SOURCE_SEARCH_PATH_NAME not in paths:
            raise ValidationError(
                _("No path in data source named {path} is configured!").format(
                    path=DATA_SOURCE_SEARCH_PATH_NAME
                )
            )

        if DATA_SOURCE_AUTH_PATH_NAME not in paths:
            raise ValidationError(
                _("No path in data source named {path} is configured!").format(
                    path=DATA_SOURCE_AUTH_PATH_NAME
                )
            )

        return paths

    def get_crvs_search_url(self, paths):
        url = self.data_source_id.url
        search_path = paths.get(DATA_SOURCE_SEARCH_PATH_NAME)

        return f"{url}{search_path}"

    def get_crvs_auth_url(self, paths):
        url = self.data_source_id.url
        auth_path = paths.get(DATA_SOURCE_AUTH_PATH_NAME)

        grant_type = self.env["ir.config_parameter"].sudo().get_param("crvs_grant_type")
        client_id = self.env["ir.config_parameter"].sudo().get_param("crvs_client_id")
        client_secret = (
            self.env["ir.config_parameter"].sudo().get_param("crvs_client_secret")
        )

        url_params = {
            "grant_type": grant_type,
            "client_id": client_id,
            "client_secret": client_secret,
        }

        return f"{url}{auth_path}?{urlencode(url_params)}"

    def get_auth_token(self, auth_url):
        headers = self.get_headers_for_request()

        response = requests.post(
            auth_url,
            headers=headers,
            timeout=self.TIMEOUT,
        )
        if response.ok:
            result = response.json()
            return f'{result.get("token_type")} {result.get("access_token")}'
        else:
            raise ValidationError(_(response.reason))

    def get_headers_for_request(self):
        return {
            "Content-Type": "application/json",
        }

    def get_header_for_body(self, crvs_version, today_isoformat, message_id):
        sender_id = "sender1"
        receiver_id = "receiver1"
        total_count = 10
        return {
            "version": crvs_version,
            "message_id": message_id,
            "message_ts": today_isoformat,
            "action": "search",
            "sender_id": sender_id,
            "sender_uri": "",
            "receiver_id": receiver_id,
            "total_count": total_count,
            "encryption_algorithm": "",
        }

    def get_query(self):
        query = []
        domain = safe_eval.safe_eval(self.domain)

        birthdate_expressions = {
            "gt": {},
            "condition": "and",
            "lt": {},
        }

        location_expression = {}

        for dom in domain:
            if isinstance(dom, list):
                field_name = constants.FIELD_MAPPING.get(dom[0])
                operator = constants.OPERATION_MAPPING.get(dom[1])
                if field_name and operator:
                    value = dom[2]
                    if dom[0] == "birthdate" and value:
                        birthdate_expressions.get(operator, {}).update(
                            {
                                "attribute_name": field_name,
                                "operator": operator,
                                "attribute_value": value,
                            }
                        )
                    if dom[0] == "location" and value:
                        location_expression.update(
                            {
                                "attribute_name": field_name,
                                "operator": operator,
                                "attribute_value": value,
                            }
                        )

        errors = []

        # Birthdate Range query
        if any([birthdate_expressions.get("gt"), birthdate_expressions.get("lt")]):
            if not birthdate_expressions.get("gt"):
                errors.append(_("Add filter for greater than birthdate!"))
            if not birthdate_expressions.get("lt"):
                errors.append(_("Add filter for less than birthdate!"))

            if not errors:
                query.append(
                    {
                        "expression1": birthdate_expressions["gt"],
                        "condition": birthdate_expressions["condition"],
                        "expression2": birthdate_expressions["lt"],
                    }
                )

        if errors:
            raise ValidationError("\n".join(errors))

        if location_expression:
            query.append({"expression1": location_expression})

        if not query:
            raise ValidationError(
                _(
                    "Add birthdate filter with one greater than and one less than or a location."
                )
            )

        return query

    def get_search_request(self, reference_id, today_isoformat):
        search_requests = {
            "reference_id": reference_id,
            "timestamp": today_isoformat,
            "search_criteria": {
                "reg_type": "ocrvs:registry_type:birth",
                "query_type": constants.PREDICATE,
                "query": self.get_query(),
            },
        }

        return search_requests

    def get_message(self, today_isoformat, transaction_id, reference_id):
        # Define Search Requests
        search_request = self.get_search_request(reference_id, today_isoformat)

        return {
            "transaction_id": transaction_id,
            "search_request": [search_request],
        }

    def get_data(self, signature, header, message):
        return {
            # "signature": signature,
            "header": header,
            "message": message,
        }

    def get_partner_and_clean_identifier(self, identifiers):
        clean_identifiers = []
        partner_id = None
        # get existing record if there's any
        for identifier in identifiers:
            identifier_type = identifier.get("name", "")
            identifier_value = identifier.get("identifier", "")
            if identifier_type and identifier_value:

                # Check if identifier type is already created. Create record if no existing identifier type
                id_type = self.env["g2p.id.type"].search(
                    [("name", "=", identifier_type)], limit=1
                )
                if not id_type:
                    id_type = self.env["g2p.id.type"].create({"name": identifier_type})

                clean_identifiers.append(
                    {"id_type": id_type, "value": identifier_value}
                )

                if not partner_id:
                    reg_id = self.env["g2p.reg.id"].search(
                        [
                            ("id_type", "=", id_type.id),
                            ("value", "=", identifier_value),
                        ],
                        limit=1,
                    )
                    if reg_id:
                        partner_id = reg_id.partner_id

        return partner_id, clean_identifiers

    def get_full_name_format(self, family_name, given_name, middle_name):
        name = ""
        if family_name:
            name += family_name + ", "
        if given_name:
            name += given_name + " "
        if middle_name:
            name += middle_name + " "
        name = name.upper()

        return name

    def get_individual_data(self, record):
        family_name = record.get("familyName", "")
        given_name = record.get("givenName", "")
        middle_name = record.get("middleName", "")
        sex = record.get("sex", "")
        birth_date = record.get("birthDate", "")
        birth_place = record.get("birthPlace", {}).get("address", "")
        try:
            birth_date = parser.parse(birth_date)
        except Exception as e:
            birth_date = False
            _logger.error(e)

        name = self.get_full_name_format(family_name, given_name, middle_name)

        return {
            "name": name,
            "family_name": family_name,
            "given_name": given_name,
            "addl_name": middle_name,
            "gender": sex.title(),
            "birthdate": birth_date,
            "birth_place": birth_place,
            "is_registrant": True,
            "is_group": False,
        }

    def create_or_update_individual(self, partner_id, partner_data):
        if partner_id:
            partner_id.write(partner_data)
        else:
            partner_id = self.env["res.partner"].create(partner_data)

        return partner_id

    def create_registrant_id(self, clean_identifiers, partner_id):
        for clean_identifier in clean_identifiers:
            partner_reg_id = self.env["g2p.reg.id"].search(
                [
                    ("id_type", "=", clean_identifier["id_type"].id),
                    ("partner_id", "=", partner_id.id),
                ]
            )
            if not partner_reg_id:
                reg_data = {
                    "id_type": clean_identifier["id_type"].id,
                    "partner_id": partner_id.id,
                    "value": clean_identifier["value"],
                }
                self.env["g2p.reg.id"].create(reg_data)
        return

    def process_records(self, record):
        identifiers = record.get("identifier", [])
        (
            partner_id,
            clean_identifiers,
        ) = self.get_partner_and_clean_identifier(identifiers)

        if partner_id:
            is_created = False
        else:
            is_created = True

        # Instantiate individual data
        partner_data = self.get_individual_data(record)

        partner_data.update({"data_source_id": self.data_source_id.id})

        # Create or Update individual
        partner_id = self.create_or_update_individual(partner_id, partner_data)

        # Check and Create Registrant ID
        self.create_registrant_id(clean_identifiers, partner_id)

        # Create CRVS Imported Individuals
        crvs_imported_individuals = self.env["spp.crvs.imported.individuals"]
        if not crvs_imported_individuals.search(
            [("fetch_crvs_id", "=", self.id), ("individual_id", "=", partner_id.id)],
            limit=1,
        ):
            crvs_imported_individuals.create(
                {
                    "fetch_crvs_id": self.id,
                    "individual_id": partner_id.id,
                    "is_created": is_created,
                    "is_updated": not is_created,
                }
            )

        return partner_id

    def fetch_crvs_beneficiary(self):

        config_parameters = self.env["ir.config_parameter"].sudo()
        today_isoformat = datetime.now(timezone.utc).isoformat()
        crvs_version = config_parameters.get_param("crvs_version")

        message_id = str(uuid.uuid4())

        # Define Data Source
        paths = self.get_data_source_paths()

        # Define CRVS auth url

        full_crvs_auth_url = self.get_crvs_auth_url(paths)

        # Retrieve auth token
        auth_token = self.get_auth_token(full_crvs_auth_url)

        # Define CRVS search url
        full_crvs_search_url = self.get_crvs_search_url(paths)

        # Define headers for post request
        headers = self.get_headers_for_request()

        headers.update({"Authorization": auth_token})

        # Define header
        header = self.get_header_for_body(
            crvs_version,
            today_isoformat,
            message_id,
        )

        # Define message
        message = self.get_message(
            today_isoformat,
            transaction_id=message_id,
            reference_id="",
        )

        # Define signature / Signature is not being used right now hence commented
        # signature = calculate_signature(header=header, payload=message)
        signature = ""

        # Define data
        data = self.get_data(
            signature,
            header,
            message,
        )

        data = json.dumps(data)

        # POST Request
        response = requests.post(
            full_crvs_search_url,
            headers=headers,
            data=data,
            timeout=self.TIMEOUT,
        )

        # Process response
        if response.ok:
            kind = "success"
            message = _("Successfully Imported CRVS Beneficiaries")

            search_responses = (
                response.json().get("message", {}).get("search_response", [])
            )
            if not search_responses:
                kind = "warning"
                message = _("No imported beneficiary")
            for search_response in search_responses:
                reg_records = search_response.get("data", {}).get("reg_records", [])
                for record in reg_records:
                    identifiers = record.get("identifier", [])
                    if identifiers:
                        partner_id = self.process_records(record)

                        relations = record.get("relations", [])
                        for relation in relations:
                            relation_identifiers = relation.get("identifier", [])
                            is_mother = "Mother" in relation.get("@type", "")
                            if relation_identifiers and is_mother:
                                relation_partner_id = self.process_records(relation)

                                # Check if parent have group membership
                                group = None
                                if relation_partner_id.individual_membership_ids:
                                    membership = self.env[
                                        "g2p.group.membership"
                                    ].search(
                                        [
                                            (
                                                "id",
                                                "in",
                                                relation_partner_id.individual_membership_ids.ids,
                                            ),
                                            ("is_created_from_crvs", "=", True),
                                        ],
                                        limit=1,
                                    )
                                    if membership:
                                        group = membership.group
                                        group.write(
                                            {
                                                "data_source_id": self.data_source_id.id,
                                            }
                                        )

                                # Create group membership
                                if not group:
                                    group = self.env["res.partner"].create(
                                        {
                                            "name": str(
                                                relation_partner_id.family_name
                                            ).title(),
                                            "is_registrant": True,
                                            "is_group": True,
                                            "grp_is_created_from_crvs": True,
                                            "data_source_id": self.data_source_id.id,
                                            "kind": self.env.ref(
                                                "g2p_registry_group.group_kind_family"
                                            ).id,
                                        }
                                    )

                                    # if parent not in group
                                    if not self.env["g2p.group.membership"].search(
                                        [
                                            ("group", "=", group.id),
                                            ("individual", "=", relation_partner_id.id),
                                        ]
                                    ):
                                        # Add parent to group
                                        self.env["g2p.group.membership"].create(
                                            {
                                                "group": group.id,
                                                "individual": relation_partner_id.id,
                                                "kind": [
                                                    (
                                                        4,
                                                        self.env.ref(
                                                            "g2p_registry_membership.group_membership_kind_head"
                                                        ).id,
                                                    )
                                                ],
                                            }
                                        )

                                # If child not in group
                                if not self.env["g2p.group.membership"].search(
                                    [
                                        ("group", "=", group.id),
                                        ("individual", "=", partner_id.id),
                                    ]
                                ):
                                    # Add child to group
                                    self.env["g2p.group.membership"].create(
                                        {
                                            "group": group.id,
                                            "individual": partner_id.id,
                                        }
                                    )

            self.done_imported = True
        else:
            kind = "danger"
            message = (
                response.json().get("error", {}).get("message", "") or response.reason
            )

        action = {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("CRVS"),
                "message": message,
                "sticky": True,
                "type": kind,
                "next": {
                    "type": "ir.actions.act_window_close",
                },
            },
        }
        return action

    def enable_fetch(self):
        self.ensure_one()

        self.done_imported = False

        action = {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Enabled Fetch button"),
                "message": _("Fetch on this criteria is now enabled."),
                "sticky": True,
                "type": "success",
                "next": {
                    "type": "ir.actions.act_window_close",
                },
            },
        }
        return action
