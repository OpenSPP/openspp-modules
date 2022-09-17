# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models
from odoo.exceptions import ValidationError


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
    id_type = fields.Many2one("g2p.id.type")


class OpenG2PIDType(models.Model):
    _inherit = "g2p.id.type"

    target_type = fields.Selection(
        [("individual", "Individual"), ("group", "Group"), ("both", "Both")],
        "Target Type",
        default="individual",
    )

    def unlink(self):
        for rec in self:
            external_identifier = self.env["ir.model.data"].search(
                [("res_id", "=", rec.id), ("model", "=", "g2p.id.type")]
            )
            if external_identifier.name == "id_type_idpass":
                raise ValidationError(_("Can't delete default ID Type"))
            else:
                return super(OpenG2PIDType, self).unlink()

    def write(self, vals):
        external_identifier = self.env["ir.model.data"].search(
            [("res_id", "=", self.id), ("model", "=", "g2p.id.type")]
        )
        if external_identifier.name == "id_type_idpass":
            raise ValidationError(_("Can't edit default ID Type"))
        else:
            return super(OpenG2PIDType, self).write(vals)
