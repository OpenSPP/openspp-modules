# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SPPCreateEventFarmWizard(models.TransientModel):
    _name = "spp.create.event.farm.wizard"
    _description = "Create Farm Event Wizard"

    event_id = fields.Many2one("spp.event.data")

    no_hh_member = fields.Integer("No. of HH Member")
    no_indigenous = fields.Integer("No. of Indigenous")
    percent_indigenous = fields.Float("% of Indigenous")
    no_15_35 = fields.Integer("No. of Member in 15-35")
    percent_15_35 = fields.Float("% of Member in 15-35")
    no_woman_headed = fields.Integer("No. of Woman-headed HH")
    no_better_off = fields.Integer("No. of Better-off HH")
    no_medium = fields.Integer("No. of Medium HH")
    no_poor = fields.Integer("No. of Poor HH")
    no_male = fields.Integer("No. of Male")
    no_female = fields.Integer("No. of Female")
    no_both = fields.Integer("No. of Both")

    def create_event(self):
        for rec in self:
            vals_list = [
                {
                    "no_hh_member": rec.no_hh_member or 0,
                    "no_indigenous": rec.no_indigenous or 0,
                    "percent_indigenous": rec.percent_indigenous or 0,
                    "no_15_35": rec.no_15_35 or 0,
                    "percent_15_35": rec.percent_15_35 or 0,
                    "no_woman_headed": rec.no_woman_headed or 0,
                    "no_better_off": rec.no_better_off or 0,
                    "no_medium": rec.no_medium or 0,
                    "no_poor": rec.no_poor or 0,
                    "no_male": rec.no_male or 0,
                    "no_female": rec.no_female or 0,
                    "no_both": rec.no_both or 0,
                }
            ]
            event = self.env["spp.event.farm"].create(vals_list)
            rec.event_id.res_id = event.id

            return event
