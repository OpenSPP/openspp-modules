# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class G2PRegistrant(models.Model):
    _inherit = "res.partner"

    full_address = fields.Text(compute="_compute_address")

    @api.depends("street", "street2", "city", "zip")
    def _compute_address(self):
        for rec in self:
            full_address = ""
            if rec.street:
                full_address = rec.street
            if rec.street2:
                full_address += f" {rec.street2}"
            if rec.city:
                full_address += f" {rec.city}"
            if rec.zip:
                full_address += f" {rec.zip}"
            rec.full_address = full_address
