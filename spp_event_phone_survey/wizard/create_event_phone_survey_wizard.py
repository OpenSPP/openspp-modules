# Part of OpenG2P. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SPPCreateEventPhoneSurveyWizard(models.TransientModel):
    _name = "spp.create.event.phone.survey.wizard"
    _description = "Create Event Phone Survey Wizard"

    registrant = fields.Many2one(
        "res.partner", domain=[("is_group", "=", True), ("is_registrant", "=", True)]
    )
    summary = fields.Char()
    description = fields.Text()

    def create_event(self):
        for rec in self:
            if rec.registrant.active_phone_survey:
                rec.registrant.end_active_event(rec.registrant.active_phone_survey)

            vals_list = [
                {
                    "registrant": rec.registrant.id,
                    "description": rec.description or False,
                    "summary": rec.summary or False,
                }
            ]
            self.env["spp.event.phone.survey"].create(vals_list)
