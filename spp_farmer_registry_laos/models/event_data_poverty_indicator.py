from odoo import api, fields, models


class OpenSPPEventDataPovertyIndicator(models.Model):
    _name = "spp.event.poverty.indicator"
    _description = "III. Poverty Indicator"

    survey_sched = fields.Selection(
        [("1", "Baseline"), ("2", "Midline"), ("3", "Endline")],
        string="Survey Schedule",
    )
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

    def get_view_id(self):
        """
        This retrieves the View ID of this model
        """
        return self.env["ir.ui.view"].search([("model", "=", self._name), ("type", "=", "form")], limit=1).id


class OpenSPPEventDataPovertyIndicatorResPartner(models.Model):
    _inherit = "res.partner"

    active_event_poverty_indicator = fields.Many2one(
        "spp.event.poverty.indicator",
        compute="_compute_active_event_poverty_indicator",
        store=True
    )

    iii_survey_schedule = fields.Selection(
        string="Survey Schedule", related="active_event_poverty_indicator.survey_sched"
    )
    iii_type_of_housing = fields.Selection(
        string="Type of Housing", related="active_event_poverty_indicator.type_of_housing"
    )
    iii_atleast_1household_member_completed_sch = fields.Selection(
        string="At least one household member completed compulsory school",
        related="active_event_poverty_indicator.atleast_1household_member_completed_sch",
    )
    iii_there_are_children_attend_pri_sch = fields.Selection(
        string="There are children attend primary school",
        related="active_event_poverty_indicator.there_are_children_attend_pri_sch",
    )
    iii_there_are_children_attend_mid_sch = fields.Selection(
        string="There are children attend middle school",
        related="active_event_poverty_indicator.there_are_children_attend_mid_sch",
    )
    iii_access_to_electricity = fields.Selection(
        string="Access to Electricity", related="active_event_poverty_indicator.access_to_electricity"
    )
    iii_access_to_basic_health_care = fields.Selection(
        string="Access to Basic Health Care", related="active_event_poverty_indicator.access_to_basic_health_care"
    )
    iii_access_to_internet = fields.Selection(
        string="Access to Internet", related="active_event_poverty_indicator.access_to_internet"
    )

    @api.depends("event_data_ids")
    def _compute_active_event_poverty_indicator(self):
        """
        This computes the active Poverty Indicator event of the group
        """
        for rec in self:
            event_data = rec._get_active_event_id("spp.event.poverty.indicator")
            rec.active_event_poverty_indicator = None
            if event_data:
                event_data_res_id = self.env["spp.event.data"].search([("id", "=", event_data)], limit=1).res_id
                rec.active_event_poverty_indicator = (
                    self.env["spp.event.poverty.indicator"].search([("id", "=", event_data_res_id)], limit=1).id
                )
