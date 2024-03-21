# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class OpenSPPStatisticsCycle(models.Model):
    _name = "spp.event.cycle"
    _description = "Event Cycle"

    program_id = fields.Many2one("g2p.program", "Program")
    cycle_id = fields.Many2one("g2p.cycle", "Cycle")
    event_type = fields.Selection(
        [
            ("fgmemr1", "FG member in round 1"),
            ("wumem", "WU member, but not received production grant"),
            ("fgmemr2", "FG member in round 2"),
            ("impagri", "Implementation of agriculture production grants (round 1)"),
            ("implive", "Implementation of livestock production grants (round 1)"),
        ],
        default="fgmemr1",
        string="Event Type",
    )
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
    no_implemented = fields.Integer("No. of Implemented")
    no_on_going = fields.Integer("No. of On-going")
    no_not_implemented = fields.Integer("No. of Not Implemented")
    production_area = fields.Float("Production Area (ha)")
    agricultural_yield = fields.Float("Agricultural Yield (ton)")
    agricultural_productivity = fields.Float("Agricultural Productivity (ton/ha)")
    no_livestock_project = fields.Integer("No. of Livestock provided by project")
    no_livestock_present = fields.Integer("No. of Livestock at present")
    no_livestock_consumption = fields.Integer("No. of Livestock consumption")
    no_livestock_sold = fields.Integer("No. of Livestock sold")
    no_livestock_increase = fields.Integer("No. of Livestock increase")

    def get_view_id(self):
        """
        This retrieves the View ID of this model
        """
        return self.env["ir.ui.view"].search([("model", "=", self._name), ("type", "=", "form")], limit=1).id
