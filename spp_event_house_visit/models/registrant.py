# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class OpenSPPRegistrant(models.Model):
    _inherit = "res.partner"

    house_visit_ids = fields.One2many(
        "spp.event.house.visit", "registrant", "House Visit IDs"
    )
    active_house_visit = fields.Many2one(
        "spp.event.data", compute="_compute_active_house_visit"
    )

    @api.depends("house_visit_ids")
    def _compute_active_house_visit(self):
        for rec in self:
            rec.active_house_visit = rec._compute_active_event("spp.event.house.visit")
