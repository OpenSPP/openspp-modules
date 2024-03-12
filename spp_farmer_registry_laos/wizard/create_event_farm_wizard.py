# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SPPCreateEventCycle2AWizard(models.TransientModel):
    _name = "spp.create.event.cycle2a.wizard"
    _description = "FG member in round 1 Wizard"

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
            event = self.env["spp.event.cycle2a"].create(vals_list)
            rec.event_id.res_id = event.id

            return event


class SPPCreateEventCycle2BWizard(models.TransientModel):
    _name = "spp.create.event.cycle2b.wizard"
    _description = "Implementation of agriculture production grants (round 1) Wizard"

    event_id = fields.Many2one("spp.event.data")

    no_implemented = fields.Integer("No. of Implemented")
    no_on_going = fields.Integer("No. of On-going")
    no_not_implemented = fields.Integer("No. of Not Implemented")
    production_area = fields.Float("Production Area (ha)")
    agricultural_yield = fields.Float("Agricultural Yield (ton)")
    agricultural_productivity = fields.Float("Agricultural Productivity (ton/ha)")

    def create_event(self):
        for rec in self:
            vals_list = [
                {
                    "no_implemented": rec.no_implemented or 0,
                    "no_on_going": rec.no_on_going or 0,
                    "no_not_implemented": rec.no_not_implemented or 0,
                    "production_area": rec.production_area or 0,
                    "agricultural_yield": rec.agricultural_yield or 0,
                    "agricultural_productivity": rec.agricultural_productivity or 0,
                }
            ]
            event = self.env["spp.event.cycle2b"].create(vals_list)
            rec.event_id.res_id = event.id

            return event


class SPPCreateEventCycle2CWizard(models.TransientModel):
    _name = "spp.create.event.cycle2c.wizard"
    _description = "Implementation of livestock production grants (round 1) Wizard"

    event_id = fields.Many2one("spp.event.data")

    no_livestock_project = fields.Integer("No. of Livestock provided by project")
    no_livestock_present = fields.Integer("No. of Livestock at present")
    no_livestock_consumption = fields.Integer("No. of Livestock consumption")
    no_livestock_sold = fields.Integer("No. of Livestock sold")
    no_livestock_increase = fields.Integer("No. of Livestock increase")

    def create_event(self):
        for rec in self:
            vals_list = [
                {
                    "no_livestock_project": rec.no_livestock_project or 0,
                    "no_livestock_present": rec.no_livestock_present or 0,
                    "no_livestock_consumption": rec.no_livestock_consumption or 0,
                    "no_livestock_sold": rec.no_livestock_sold or 0,
                    "no_livestock_increase": rec.no_livestock_increase or 0,
                }
            ]
            event = self.env["spp.event.cycle2c"].create(vals_list)
            rec.event_id.res_id = event.id

            return event


class SPPCreateEventCycle3AWizard(models.TransientModel):
    _name = "spp.create.event.cycle3a.wizard"
    _description = "WU member, but not received production grant Wizard"

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
            event = self.env["spp.event.cycle3a"].create(vals_list)
            rec.event_id.res_id = event.id

            return event


class SPPCreateEventCycle3BWizard(models.TransientModel):
    _name = "spp.create.event.cycle3b.wizard"
    _description = "FG member in round 2"

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
            event = self.env["spp.event.cycle3b"].create(vals_list)
            rec.event_id.res_id = event.id

            return event
