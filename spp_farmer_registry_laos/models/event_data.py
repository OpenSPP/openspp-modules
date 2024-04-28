# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


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


class OpenSPPStatisticsCycleResPartner(models.Model):
    _inherit = "res.partner"

    active_event_cycle = fields.Many2one(
        "spp.event.cycle",
        compute="_compute_active_event_cycle",
        store=True
    )

    statistics_program_id = fields.Many2one("g2p.program", "Program", related="active_event_cycle.program_id")
    statistics_cycle_id = fields.Many2one("g2p.cycle", "Cycle", related="active_event_cycle.cycle_id")
    statistics_event_type = fields.Selection(string="Event Type", related="active_event_cycle.event_type")
    statistics_no_hh_member = fields.Integer("No. of HH Member", related="active_event_cycle.no_hh_member")
    statistics_no_indigenous = fields.Integer("No. of Indigenous", related="active_event_cycle.no_indigenous")
    statistics_percent_indigenous = fields.Float("% of Indigenous", related="active_event_cycle.percent_indigenous")
    statistics_no_15_35 = fields.Integer("No. of Member in 15-35", related="active_event_cycle.no_15_35")
    statistics_percent_15_35 = fields.Float("% of Member in 15-35", related="active_event_cycle.percent_15_35")
    statistics_no_woman_headed = fields.Integer("No. of Woman-headed HH", related="active_event_cycle.no_woman_headed")
    statistics_no_better_off = fields.Integer("No. of Better-off HH", related="active_event_cycle.no_better_off")
    statistics_no_medium = fields.Integer("No. of Medium HH", related="active_event_cycle.no_medium")
    statistics_no_poor = fields.Integer("No. of Poor HH", related="active_event_cycle.no_poor")
    statistics_no_male = fields.Integer("No. of Male", related="active_event_cycle.no_male")
    statistics_no_female = fields.Integer("No. of Female", related="active_event_cycle.no_female")
    statistics_no_both = fields.Integer("No. of Both", related="active_event_cycle.no_both")
    statistics_no_implemented = fields.Integer("No. of Implemented", related="active_event_cycle.no_implemented")
    statistics_no_on_going = fields.Integer("No. of On-going", related="active_event_cycle.no_on_going")
    statistics_no_not_implemented = fields.Integer(
        "No. of Not Implemented", related="active_event_cycle.no_not_implemented"
    )
    statistics_production_area = fields.Float("Production Area (ha)", related="active_event_cycle.production_area")
    statistics_agricultural_yield = fields.Float(
        "Agricultural Yield (ton)", related="active_event_cycle.agricultural_yield"
    )
    statistics_agricultural_productivity = fields.Float(
        "Agricultural Productivity (ton/ha)", related="active_event_cycle.agricultural_productivity"
    )
    statistics_no_livestock_project = fields.Integer(
        "No. of Livestock provided by project", related="active_event_cycle.no_livestock_project"
    )
    statistics_no_livestock_present = fields.Integer(
        "No. of Livestock at present", related="active_event_cycle.no_livestock_present"
    )
    statistics_no_livestock_consumption = fields.Integer(
        "No. of Livestock consumption", related="active_event_cycle.no_livestock_consumption"
    )
    statistics_no_livestock_sold = fields.Integer(
        "No. of Livestock sold", related="active_event_cycle.no_livestock_sold"
    )
    statistics_no_livestock_increase = fields.Integer(
        "No. of Livestock increase", related="active_event_cycle.no_livestock_increase"
    )

    @api.depends("event_data_ids")
    def _compute_active_event_cycle(self):
        """
        This computes the active Statistics cycle event of the group
        """
        for rec in self:
            event_data = rec._get_active_event_id("spp.event.cycle")
            rec.active_event_cycle = None
            if event_data:
                event_data_res_id = self.env["spp.event.data"].search([("id", "=", event_data)], limit=1).res_id
                rec.active_event_cycle = (
                    self.env["spp.event.cycle"].search([("id", "=", event_data_res_id)], limit=1).id
                )
