# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class SPPCreateEventFoodSecurityWizard(models.TransientModel):
    _name = "spp.create.event.food.security.wizard"
    _description = "VII. Food Security"

    event_id = fields.Many2one("spp.event.data")
    survey_sched = fields.Selection(
        [("1", "Baseline"), ("2", "Midline"), ("3", "Endline")],
        string="Survey Schedule",
    )
    hungry_season_past_12 = fields.Integer("Experience a Hungry season in the past 12 months")
    shortage_january = fields.Integer("January")
    shortage_february = fields.Integer("February")
    shortage_march = fields.Integer("March")
    shortage_april = fields.Integer("April")
    shortage_may = fields.Integer("May")
    shortage_june = fields.Integer("June")
    shortage_july = fields.Integer("July")
    shortage_august = fields.Integer("August")
    shortage_september = fields.Integer("September")
    shortage_october = fields.Integer("October")
    shortage_november = fields.Integer("November")
    shortage_december = fields.Integer("December")

    def create_event(self):
        for rec in self:
            vals_list = {
                "hungry_season_past_12": rec.hungry_season_past_12,
                "shortage_january": rec.shortage_january,
                "shortage_february": rec.shortage_february,
                "shortage_march": rec.shortage_march,
                "shortage_april": rec.shortage_april,
                "shortage_may": rec.shortage_may,
                "shortage_june": rec.shortage_june,
                "shortage_july": rec.shortage_july,
                "shortage_august": rec.shortage_august,
                "shortage_september": rec.shortage_september,
                "shortage_october": rec.shortage_october,
                "shortage_november": rec.shortage_november,
                "shortage_december": rec.shortage_december,
                "survey_sched": rec.survey_sched,
            }

            event = self.env["spp.event.food.security"].create(vals_list)
            rec.event_id.res_id = event.id

            return event
