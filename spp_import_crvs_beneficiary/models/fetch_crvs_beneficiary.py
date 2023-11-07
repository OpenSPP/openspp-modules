import logging

import requests
from dateutil import parser

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from ..models import constants

_logger = logging.getLogger(__name__)


class SPPFetchCRVSBeneficiary(models.Model):
    _name = "spp.fetch.crvs.beneficiary"
    _description = "Fetch CRVS Beneficiary"

    name = fields.Char(compute="_compute_name")
    filter_type = fields.Selection(
        constants.FILTER_TYPE_CHOICES,
        required=True,
        string="Type",
    )
    start_date = fields.Date()
    end_date = fields.Date()
    identifier_type = fields.Selection(constants.ID_TYPE_CHOICES)
    identifier_value = fields.Char()

    done_imported = fields.Boolean()
    imported_individual_ids = fields.One2many(
        "spp.crvs.imported.individuals", "fetch_crvs_id", "Imported Individuals"
    )

    TIMEOUT = 10

    @api.depends("filter_type")
    def _compute_name(self):
        for rec in self:
            if rec.filter_type == constants.ID_TYPE:
                rec.name = f"{constants.ID_TYPE_LABEL}: {rec.identifier_type} - {rec.identifier_value}"
            elif rec.filter_type == constants.BIRTHDATE_RANGE:
                rec.name = f"{constants.BIRTHDATE_RANGE_LABEL}: {rec.start_date} - {rec.end_date}"

    @api.constrains("filter_type")
    def _check_filter_type(self):
        for rec in self:
            if rec.filter_type == constants.ID_TYPE:
                if not rec.identifier_type or not rec.identifier_value:
                    raise ValidationError(
                        _(
                            "Identifier Type and Identifier Value is required if selected Type is %(label)s"
                        )
                        % {
                            "label": constants.ID_TYPE_LABEL,
                        }
                    )
            elif rec.filter_type == constants.BIRTHDATE_RANGE:
                if not rec.start_date or not rec.end_date:
                    raise ValidationError(
                        _(
                            "Start Date and End Date is required if selected Type is %(label)s"
                        )
                        % {
                            "label": constants.BIRTHDATE_RANGE_LABEL,
                        }
                    )
        return

    def get_crvs_search_url(self, config_parameters):
        CRVS_URL = config_parameters.get_param("crvs_url")
        CRVS_NAMESPACE = config_parameters.get_param("crvs_namespace")
        CRVS_VERSION = config_parameters.get_param("crvs_version")
        SEARCH_PATH = "/registry/sync/search"

        return f"{CRVS_URL}/{CRVS_NAMESPACE}/v{CRVS_VERSION}/{SEARCH_PATH}"

    def get_query(self):
        query_type = constants.QUERY_TYPE_MAPPING[self.filter_type]
        query = ""
        if query_type == constants.ID_TYPE_VALUE:
            query = {
                "identifier_type": {"value": self.identifier_type},
                "identifier_value": self.identifier_value,
            }
        elif query_type == constants.PREDICATE:
            if self.filter_type == constants.BIRTHDATE_RANGE:
                query = [
                    {
                        "condition": "and",
                        "expression1": {
                            "attribute_name": "birthdate",
                            "operator": "gt",
                            "attribute_value": str(self.start_date),
                        },
                        "expression2": {
                            "attribute_name": "birthdate",
                            "operator": "lt",
                            "attribute_value": str(self.end_date),
                        },
                    }
                ]

        return query

    def get_headers_for_request(self):
        return {
            "Content-Type": "application/json",
        }

    def get_header_for_body(self, crvs_version, today_isoformat):
        message_id = "message1"
        sender_id = "sender1"
        receiver_id = "receiver1"
        total_count = 1
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

    def get_message(self, crvs_version, today_isoformat, query):
        query_type = constants.QUERY_TYPE_MAPPING[self.filter_type]
        transaction_id = "123456"
        reference_id = "1234567"
        return {
            "transaction_id": transaction_id,
            "search_request": [
                {
                    "version": crvs_version,
                    "reference_id": reference_id,
                    "timestamp": today_isoformat,
                    "registry_type": "civil",
                    "search_criteria": {
                        "reg_event_type": {"value": "1"},
                        "query_type": query_type,
                        "query": query,
                        "result_record_type": {"value": "person"},
                    },
                }
            ],
        }

    def get_data(self, signature, header, message):
        return {"signature": signature, "header": header, "message": message}

    def get_partner_and_clean_identifier(self, identifiers):
        clean_identifiers = []
        partner_id = None
        # get existing record if there's any
        for identifier in identifiers:
            identifier_type = identifier.get("type", "")
            identifier_value = identifier.get("value", "")
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
        family_name = record.get("family_name", "")
        given_name = record.get("given_name", "")
        middle_name = record.get("middle_name", "")
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

    def fetch_crvs_beneficiary(self):
        config_parameters = self.env["ir.config_parameter"].sudo()
        today_isoformat = fields.Datetime.today().isoformat()
        crvs_version = config_parameters.get_param("crvs_version")

        # Define CRVS search url
        full_crvs_search_url = self.get_crvs_search_url(config_parameters)

        # Define headers for post request
        headers = self.get_headers_for_request()

        # Define query
        query = self.get_query()

        # Define header
        header = self.get_header_for_body(crvs_version, today_isoformat)

        # Define message
        message = self.get_message(crvs_version, today_isoformat, query)

        # Define signature
        signature = ""

        # Define data
        data = self.get_data(signature, header, message)

        # POST Request
        response = requests.post(
            full_crvs_search_url, headers=headers, json=data, timeout=self.TIMEOUT
        )

        # Process response
        if response.ok:
            kind = "success"
            message = _("Successfully Imported CRVS Beneficiaries")

            search_responses = (
                response.json().get("message", {}).get("search_response", [])
            )
            if search_responses:
                for search_response in search_responses:
                    reg_records = search_response.get("data", {}).get("reg_records", [])
                    for record in reg_records:
                        identifiers = record.get("identifier", [])
                        if identifiers:
                            # get existing record if there's any and clean identifiers for better searching in ORM
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

                            # Create or Update individual
                            partner_id = self.create_or_update_individual(
                                partner_id, partner_data
                            )

                            # Check and Create Registrant ID
                            self.create_registrant_id(clean_identifiers, partner_id)

                            # Create CRVS Imported Individuals
                            self.env["spp.crvs.imported.individuals"].create(
                                {
                                    "fetch_crvs_id": self.id,
                                    "individual_id": partner_id.id,
                                    "is_created": is_created,
                                    "is_updated": not is_created,
                                }
                            )
                self.done_imported = True
        else:
            kind = "danger"
            message = response.reason

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
