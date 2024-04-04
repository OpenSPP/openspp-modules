# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SPPCreateEventWashIndicatorsWizard(models.TransientModel):
    _name = "spp.create.event.wash.ind.wizard"
    _description = "XV. WASH Indicators"

    event_id = fields.Many2one("spp.event.data")
    survey_sched = fields.Selection(
        [("1", "Baseline"), ("2", "Midline"), ("3", "Endline")],
        string="Survey Schedule",
    )
    water_sources = fields.Selection(
        [
            ("1", "Safety Managed"),
            ("2", "Basic"),
            ("3", "Limited"),
            ("4", "Unimproved"),
            ("5", "Surface Water"),
        ]
    )
    latrine_condition = fields.Selection(
        [
            ("1", "Safety Managed"),
            ("2", "Basic"),
            ("3", "Limited"),
            ("4", "Unimproved"),
            ("5", "Open Defecation"),
        ]
    )
    handwashing_facility = fields.Selection(
        [
            ("1", "Basic"),
            ("2", "Limited"),
            ("3", "No Facility"),
        ]
    )

    def create_event(self):
        for rec in self:
            vals_list = {
                "water_sources": rec.water_sources,
                "latrine_condition": rec.latrine_condition,
                "handwashing_facility": rec.handwashing_facility,
                "survey_sched": rec.survey_sched,
            }

            event = self.env["spp.event.wash.ind"].create(vals_list)
            rec.event_id.res_id = event.id

            return event
