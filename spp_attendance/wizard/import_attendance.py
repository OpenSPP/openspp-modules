# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import copy

import requests

from odoo import _, fields, models
from odoo.exceptions import UserError

DEFAULT_RAW_BODY_FOR_AUTH = """{
    "client_id": "<insert client id>",
    "client_secret": "<insert client id>",
    "grant_type": "client_credentials",
    "db_name": "<insert db name>"
}"""


DEFAULT_RAW_BODY_FOR_IMPORT = """{
    "header": {
        "message_id": "123456789020211216223812",
        "message_ts": "2022-12-04T18:01:07+00:00",
        "action": "search",
        "sender_id": "https://integrating-server.com",
        "total_count": 10
    },
    "message": {
        "transaction_id": "123456789020211216223812",
        "search_request": [
            {
                "reference_id": "123456789020211216223812",
                "timestamp": "2022-12-04T17:20:07-04:00",
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

    raw_body_for_import = fields.Text(
        string="Raw Body for Import",
        required=True,
        help=_("The raw body to be sent to the import URL. Must be in JSON format."),
        default=DEFAULT_RAW_BODY_FOR_IMPORT,
    )

    def action_import_attendance(self):
        self.ensure_one()

        auth_url = self.env["ir.config_parameter"].get_param("spp_attendance.attendance_auth_url")
        try:
            r = requests.post(auth_url, data=self.raw_body)
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

        import_url = self.env["ir.config_parameter"].get_param("spp_attendance.attendance_import_url")
        try:
            header = {
                "Authorization": access_token,
                "Content-Type": "application/json",
            }
            r = requests.post(import_url, headers=header, data=self.raw_body_for_import)
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
                "next": {
                    "type": "ir.actions.act_window_close",
                },
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
