# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class OpenSPPRegistrant(models.Model):
    _inherit = "res.partner"

    phone_survey_ids = fields.One2many(
        "spp.event.phone.survey", "registrant", "Phone Survey IDs"
    )
    active_phone_survey = fields.Many2one(
        "spp.event.data", compute="_compute_active_phone_survey"
    )

    @api.depends("phone_survey_ids")
    def _compute_active_phone_survey(self):
        for rec in self:
            rec.active_phone_survey = rec._compute_active_event(
                "spp.event.phone.survey"
            )
