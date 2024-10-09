# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import copy
import json
import uuid
from urllib.parse import urlencode, urljoin

import pytz
import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError

DEFAULT_RAW_BODY_FOR_AUTH = """{
    "client_id": "<insert client id>",
    "client_secret": "<insert client secret>",
    "grant_type": "client_credentials",
    "db_name": "<insert db name>"
}"""


DEFAULT_RAW_BODY_FOR_IMPORT = """{
    "header": {
        "message_id": "%(message_id)s",
        "message_ts": "%(message_ts)s",
        "action": "search",
        "sender_id": "%(sender_id)s",
        "total_count": 10
    },
    "message": {
        "transaction_id": "%(transaction_id)s",
        "search_request": [
            {
                "reference_id": "%(reference_id)s",
                "timestamp": "%(timestamp)s",
                "search_criteria": {
                    "reg_type": "SPP:RegistryType:Individual",
                    "query_type": "predicate",
                    "query": []
                }
            }
        ]
    }
}"""


class ImportAttendanceWiz(models.TransientModel):
    _name = "spp.import.attendance.wizard"
    _description = "Import Attendance Wizard"

    @api.model
    def _get_default_raw_body_for_import(self):
        tz = self._context.get("tz") or self.env.user.tz or "UTC"
        local = pytz.timezone(tz)

        current_datetime = local.localize(fields.Datetime.now())

        formatted_datetime = current_datetime.strftime("%Y-%m-%dT%H:%M:%S%z")
        return DEFAULT_RAW_BODY_FOR_IMPORT % {
            "message_id": uuid.uuid4(),
            "transaction_id": uuid.uuid4(),
            "reference_id": uuid.uuid4(),
            "timestamp": formatted_datetime,
            "message_ts": formatted_datetime,
            "sender_id": self.env["ir.config_parameter"].get_param("web.base.url"),
        }

    auth_type = fields.Selection(
        selection=[("Basic", "Basic"), ("Bearer", "Bearer")],
        string="Auth Type",
        default="Bearer",
    )
    raw_body = fields.Text(
        string="Raw Body for Authentication",
        required=True,
        help=_("The raw body to be sent to the auth URL. Must be in JSON format."),
        default=DEFAULT_RAW_BODY_FOR_AUTH,
    )
    auth_header = fields.Text(string="Auth Headers", default="{}")

    raw_body_for_import = fields.Text(
        string="Raw Body for Import",
        required=True,
        help=_("The raw body to be sent to the import URL. Must be in JSON format."),
        default=_get_default_raw_body_for_import,
    )
    import_header = fields.Text(string="Import Headers", default="{}")
    page = fields.Integer(string="Page", default=1)
    limit = fields.Integer(string="Limit", default=30)

    def action_import_attendance(self):
        self.ensure_one()

        auth_url = self.env["ir.config_parameter"].get_param("spp_attendance.attendance_auth_url")

        try:
            auth_header = self.auth_header or "{}"
            auth_header = json.loads(auth_header)
        except json.JSONDecodeError as e:
            raise UserError(_("Auth Headers must be in JSON format")) from e

        try:
            import_header = self.import_header or "{}"
            import_header = json.loads(import_header)
        except json.JSONDecodeError as e:
            raise UserError(_("Import Headers must be in JSON format")) from e

        try:
            r = requests.post(auth_url, data=self.raw_body, headers=auth_header)
        except requests.exceptions.ConnectionError as e:
            raise UserError(_("Unable to connect to the server. Please check your internet connection.")) from e

        if not r.ok:
            raise UserError(_("Authentication failed. Reason: %s." % (r.reason)))

        access_token_mapping = self.env["ir.config_parameter"].get_param("spp_attendance.access_token_mapping")

        if access_token_mapping:
            token_mapping = access_token_mapping.split(".")
            access_token = r.json()
            for mapping in token_mapping:
                access_token = access_token.get(mapping)
        else:
            access_token = r.text

        if not access_token.startswith("Bearer") or access_token.startswith("Basic"):
            access_token = f"{self.auth_type} {access_token}"

        params = {
            "page": self.page,
            "limit": self.limit,
        }
        import_url = self.env["ir.config_parameter"].get_param("spp_attendance.attendance_import_url")
        full_import_url = urljoin(import_url, "?" + urlencode(params))

        try:
            import_header.update(
                {
                    "Authorization": access_token,
                }
            )
            if "Content-Type" not in import_header:
                import_header["Content-Type"] = "application/json"
            r = requests.post(full_import_url, headers=import_header, data=self.raw_body_for_import)
        except requests.exceptions.ConnectionError as e:
            raise UserError(_("Unable to connect to the server. Please check your internet connection.")) from e

        if not r.ok:
            raise UserError(_("Import failed. Reason: %s." % (r.reason)))

        return self._import_attendance(r.json())

    def _import_attendance(self, data):
        self.ensure_one()
        personal_informations = copy.deepcopy(data)

        missing_required_fields = self.check_required_fields(
            [
                "attendance_import_url",
                "personal_information_mapping",
                "person_identifier_mapping",
                "family_name_mapping",
                "given_name_mapping",
            ]
        )

        if missing_required_fields:
            raise UserError(_("Please fill in the following required fields: %s" % ", ".join(missing_required_fields)))

        elements = self.env["ir.config_parameter"].get_param("spp_attendance.personal_information_mapping").split(".")
        personal_informations = self.element_mapper(personal_informations, elements)

        if not isinstance(personal_informations, list):
            raise UserError(_("Personal Information Mapping must point to a list"))

        person_identifier_elements = (
            self.env["ir.config_parameter"].get_param("spp_attendance.person_identifier_mapping").split(".")
        )
        family_name_elements = (
            self.env["ir.config_parameter"].get_param("spp_attendance.family_name_mapping").split(".")
        )
        given_name_elements = self.env["ir.config_parameter"].get_param("spp_attendance.given_name_mapping").split(".")

        email_elements = []
        if email_mapping := self.env["ir.config_parameter"].get_param("spp_attendance.email_mapping"):
            email_elements = email_mapping.split(".")

        phone_elements = []
        if phone_mapping := self.env["ir.config_parameter"].get_param("spp_attendance.phone_mapping"):
            phone_elements = phone_mapping.split(".")

        imported_count = 0

        for info in personal_informations:
            person_identifier = self.element_mapper(info, person_identifier_elements)
            self.check_data_instance(person_identifier, "Person Identifier", str)

            family_name = self.element_mapper(info, family_name_elements)
            self.check_data_instance(family_name, "Family Name", str)

            given_name = self.element_mapper(info, given_name_elements)
            self.check_data_instance(given_name, "Given Name", str)

            email = self.element_mapper(info, email_elements)
            self.check_data_instance(email, "Email", str)

            phone = self.element_mapper(info, phone_elements)
            self.check_data_instance(phone, "Phone", str)

            if subscriber_id := self.env["spp.attendance.subscriber"].search(
                [("person_identifier", "=", person_identifier)], limit=1
            ):
                subscriber_id.write(
                    {
                        "family_name": family_name,
                        "given_name": given_name,
                        "email": email,
                        "phone": phone,
                    }
                )
            else:
                self.env["spp.attendance.subscriber"].create(
                    {
                        "person_identifier": person_identifier,
                        "family_name": family_name,
                        "given_name": given_name,
                        "email": email,
                        "phone": phone,
                    }
                )
                imported_count += 1

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Import"),
                "message": _("Imported %s persons.", imported_count),
                "sticky": False,
                "type": "success",
            },
        }

    def check_required_fields(self, required_fields):
        missing_required_fields = []
        for field in required_fields:
            if not self.env["ir.config_parameter"].get_param(f"spp_attendance.{field}"):
                missing_required_fields.append(self.env["ir.config_parameter"]._fields[field].string)
        return missing_required_fields

    def element_mapper(self, data, elements):
        if not elements:
            return None

        for element in elements:
            if not element.isdigit():
                if element not in data:
                    raise UserError(_("Element %s not found in data" % element))
                data = data[element]
            elif element.isdigit():
                if not isinstance(data, list):
                    raise UserError(_("Data before the index is not a list"))
                if int(element) >= len(data):
                    raise UserError(_("Index out of range"))
                data = data[int(element)]

        return data

    def check_data_instance(self, data, data_name, instance):
        if data and not isinstance(data, instance):
            raise UserError(_(f"{data_name} must be of type {str(instance)}"))
