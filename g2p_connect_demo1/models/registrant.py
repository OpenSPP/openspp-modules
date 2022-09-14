# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class G2PRegistrant(models.Model):
    _inherit = "res.partner"

    full_address = fields.Text(compute="_compute_address", string="Address")

    @api.depends("street", "street2", "city", "zip")
    def _compute_address(self):
        for rec in self:
            rec.full_address = ""
            if rec.street:
                rec.full_address = rec.street
            if rec.street2:
                rec.full_address += " " + rec.street2
            if rec.city:
                rec.full_address += " " + rec.city
            if rec.zip:
                rec.full_address += " " + rec.zip
            rec.address = rec.full_address
