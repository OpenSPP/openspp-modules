# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class OpenSPPRegistrant(models.Model):
    _inherit = "res.partner"

    active_house_visit = fields.Many2one(
        "spp.event.data", compute="_compute_active_house_visit"
    )
    active_phone_survey = fields.Many2one(
        "spp.event.data", compute="_compute_active_phone_survey"
    )

    @api.depends("event_data_ids")
    def _compute_active_house_visit(self):
        for rec in self:
            rec.active_house_visit = rec._get_active_event_id("spp.event.house.visit")

    @api.depends("event_data_ids")
    def _compute_active_phone_survey(self):
        for rec in self:
            rec.active_phone_survey = rec._get_active_event_id("spp.event.phone.survey")
