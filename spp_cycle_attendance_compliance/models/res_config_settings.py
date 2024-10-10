import json

import requests

from odoo import api, fields, models
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    @api.model
    def _get_default_attendance_auth_url(self):
        web_base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        endpoint = "/auth/token"
        return web_base_url + endpoint

    @api.model
    def _get_default_attendance_compliance_url(self):
        web_base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        endpoint = "/attendances"
        return web_base_url + endpoint

    attendance_auth_url = fields.Char(
        string="Auth URL",
        config_parameter="spp_attendance.attendance_auth_url",
        default=_get_default_attendance_auth_url,
    )
    attendance_client_id = fields.Char(
        string="Client ID",
        config_parameter="spp_attendance.attendance_client_id",
    )
    attendance_client_secret = fields.Char(
        string="Client Secret",
        config_parameter="spp_attendance.attendance_client_secret",
    )
    attendance_compliance_url = fields.Char(
        string="Compliance URL",
        config_parameter="spp_cycle_attendance_compliance.attendance_compliance_url",
        default=_get_default_attendance_compliance_url,
    )

    def test_connection(self):
        self.ensure_one()
        url = self.attendance_auth_url
        client_id = self.attendance_client_id
        client_secret = self.attendance_client_secret
        data = json.dumps({"client_id": client_id, "client_secret": client_secret})
        response = requests.post(url, data=data)
        if response.status_code == 200:
            raise UserError("Connection Successful")
        else:
            raise UserError("Connection Failed")
