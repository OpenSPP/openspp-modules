from odoo import _, fields, models


class RegistryConfig(models.TransientModel):
    _inherit = "res.config.settings"

    attendance_auth_url = fields.Char(
        string="Auth URL",
        config_parameter="spp_attendance.attendance_auth_url",
        default="http://localhost:8080/oauth2/client/token",
    )
    access_token_mapping = fields.Char(
        string="Access Token Mapping",
        config_parameter="spp_attendance.access_token_mapping",
        default="access_token",
    )
    attendance_import_url = fields.Char(
        string="Import URL",
        config_parameter="spp_attendance.attendance_import_url",
        default="http://localhost:8080/registry/sync/search",
    )

    personal_information_mapping = fields.Char(
        string="Personal Information",
        config_parameter="spp_attendance.personal_information_mapping",
        default="message.search_response.0.data.reg_records",
    )
    person_identifier_mapping = fields.Char(
        string="Person Identifier",
        config_parameter="spp_attendance.person_identifier_mapping",
        default="identifier.0.identifier",
    )
    family_name_mapping = fields.Char(
        string="Family Name",
        config_parameter="spp_attendance.family_name_mapping",
        default="familyName",
    )
    given_name_mapping = fields.Char(
        string="Given Name",
        config_parameter="spp_attendance.given_name_mapping",
        default="givenName",
    )
    email_mapping = fields.Char(string="Email", config_parameter="spp_attendance.email_mapping")
    phone_mapping = fields.Char(string="Phone", config_parameter="spp_attendance.phone_mapping")

    def action_import(self):
        self.ensure_one()

        form_id = self.env.ref("spp_attendance.import_attendance_wizard").id
        action = {
            "name": _("Import Attendance"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_id": form_id,
            "view_type": "form",
            "res_model": "spp.import.attendance.wizard",
            "target": "new",
            # "context": {
            #     "res_config_id": self.id,
            # },
        }
        return action
