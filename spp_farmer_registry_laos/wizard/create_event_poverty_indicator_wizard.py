# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class SPPCreateEventPovertyIndicatorWizard(models.TransientModel):
    _name = "spp.create.event.poverty.indicator.wizard"
    _description = "Event Poverty Indicator"

    event_id = fields.Many2one("spp.event.data")

    type_of_housing = fields.Selection([("1", "Not Permanent"), ("2", "Medium permanent"), ("3", "Permanent")])
    atleast_1household_member_completed_sch = fields.Selection(
        [("1", "Yes"), ("2", "No")], string="At least one household member completed compulsory school"
    )
    there_are_children_attend_pri_sch = fields.Selection(
        [("1", "Yes"), ("2", "No"), ("3", "N/A (I have no children aged 6-10 years)")],
        string="There are children attend primary school",
    )
    there_are_children_attend_mid_sch = fields.Selection(
        [("1", "Yes"), ("2", "No"), ("3", "N/A (I have no children aged 11-13 years)")],
        string="There are children attend middle school",
    )
    access_to_electricity = fields.Selection(
        [
            ("1", "No Electricity"),
            ("2", "Private power generation (solar panel, generator, etc.)"),
            ("3", "Connected to power grid"),
        ],
        string="Access to Electricity",
    )
    access_to_basic_health_care = fields.Selection([("1", "Yes"), ("2", "No")], string="Access to Basic Health Care")
    access_to_internet = fields.Selection(
        [
            ("1", "No, internet accesses as the area has no mobile coverage"),
            ("2", "No internet accesses as the interviewee has no mobile phone (the area has mobile coverage)"),
            ("3", "Yes, have access to internet"),
        ],
        string="Access to Internet",
    )

    def create_event(self):
        for rec in self:
            vals_list = {
                "type_of_housing": rec.type_of_housing,
                "atleast_1household_member_completed_sch": rec.atleast_1household_member_completed_sch,
                "there_are_children_attend_pri_sch": rec.there_are_children_attend_pri_sch,
                "there_are_children_attend_mid_sch": rec.there_are_children_attend_mid_sch,
                "access_to_electricity": rec.access_to_electricity,
                "access_to_basic_health_care": rec.access_to_basic_health_care,
                "access_to_internet": rec.access_to_internet,
            }

            event = self.env["spp.event.poverty.indicator"].create(vals_list)
            rec.event_id.res_id = event.id

            return event
