# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class OpenSPPIDPass(models.Model):
    _name = "spp.id.pass"
    _description = "ID Pass"

    name = fields.Char("Template Name")
    api_url = fields.Text("API URL")
    api_username = fields.Char("API Username")
    api_password = fields.Char("API Password")
    filename_prefix = fields.Char("File Name Prefix")
    expiry_length = fields.Integer("ID Expiry Length", default=1)
    expiry_length_type = fields.Selection(
        [("years", "Years"), ("months", "Months"), ("days", "Days")],
        "Length Type",
        default="years",
    )
    is_active = fields.Boolean("Active")
