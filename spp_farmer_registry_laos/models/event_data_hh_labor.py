from odoo import api, fields, models


class OpenSPPEventDataHHLabor(models.Model):
    _name = "spp.event.hh.labor"
    _description = "IV. Household Member and Labor Availability"

    survey_sched = fields.Selection(
        [("1", "Baseline"), ("2", "Midline"), ("3", "Endline")],
        string="Survey Schedule",
    )
    no_hh_members_women = fields.Integer("Number of Women in the Household")
    no_hh_members_men = fields.Integer("Number of Men in the Household")
    no_hh_members = fields.Integer("Total Number of Household Members", compute="_compute_total_hh_members")

    hh_labor_availability_15_35_women = fields.Integer(
        "Number of women labors in the household between 15 - 35 years old"
    )
    hh_labor_availability_15_35_men = fields.Integer("Number of men labors in the household between 15 - 35 years old")
    tot_hh_labor_availability_15_35 = fields.Integer(
        "Total number of labors in the household between 15 - 35 years old",
        compute="_compute_tot_hh_labor_availability_15_35",
    )

    hh_labor_availability_36_60_women = fields.Integer(
        "Number of women labors in the household between 36 - 60 years old"
    )
    hh_labor_availability_36_60_men = fields.Integer("Number of men labors in the household between 36 - 60 years old")
    tot_hh_labor_availability_36_60 = fields.Integer(
        "Total number of labors in the household between 36 - 60 years old",
        compute="_compute_tot_hh_labor_availability_36_60",
    )

    labor_availability_agri_15_35_women = fields.Integer(
        "Number of women labors in the household, between 15 - 35 years old, availability in agriculture"
    )
    labor_availability_agri_15_35_men = fields.Integer(
        "Number of men labors in the household, between 15 - 35 years old, availability in agriculture"
    )
    tot_labor_availablity_agri_15_35 = fields.Integer(
        "Total number of labors in the household, between 15 - 35 years old, availability in agriculture",
        compute="_compute_tot_labor_availablity_agri_15_35",
    )

    labor_availability_agri_36_60_women = fields.Integer(
        "Number of women labors in the household, between 36 - 60 years old, availability in agriculture"
    )
    labor_availability_agri_36_60_men = fields.Integer(
        "Number of men labors in the household, between 36 - 60 years old, availability in agriculture"
    )
    tot_labor_availablity_agri_36_60 = fields.Integer(
        "Total number of labors in the household, between 36 - 60 years old, availability in agriculture",
        compute="_compute_tot_labor_availablity_agri_36_60",
    )

    @api.depends("no_hh_members_women", "no_hh_members_men")
    def _compute_total_hh_members(self):
        for rec in self:
            rec.no_hh_members = rec.no_hh_members_women + rec.no_hh_members_men

    @api.depends("hh_labor_availability_15_35_women", "hh_labor_availability_15_35_men")
    def _compute_tot_hh_labor_availability_15_35(self):
        for rec in self:
            rec.tot_hh_labor_availability_15_35 = (
                rec.hh_labor_availability_15_35_women + rec.hh_labor_availability_15_35_men
            )

    @api.depends("hh_labor_availability_36_60_women", "hh_labor_availability_36_60_men")
    def _compute_tot_hh_labor_availability_36_60(self):
        for rec in self:
            rec.tot_hh_labor_availability_36_60 = (
                rec.hh_labor_availability_36_60_women + rec.hh_labor_availability_36_60_men
            )

    @api.depends("labor_availability_agri_15_35_women", "labor_availability_agri_15_35_men")
    def _compute_tot_labor_availablity_agri_15_35(self):
        for rec in self:
            rec.tot_labor_availablity_agri_15_35 = (
                rec.labor_availability_agri_15_35_women + rec.labor_availability_agri_15_35_men
            )

    @api.depends("labor_availability_agri_36_60_women", "labor_availability_agri_36_60_men")
    def _compute_tot_labor_availablity_agri_36_60(self):
        for rec in self:
            rec.tot_labor_availablity_agri_36_60 = (
                rec.labor_availability_agri_36_60_women + rec.labor_availability_agri_36_60_men
            )

    def get_view_id(self):
        """
        This retrieves the View ID of this model
        """
        return self.env["ir.ui.view"].search([("model", "=", self._name), ("type", "=", "form")], limit=1).id


class OpenSPPEventDataHHLaborResPartner(models.Model):
    _inherit = "res.partner"

    active_event_hh_labor = fields.Many2one(
        "spp.event.hh.labor",
        compute="_compute_active_event_hh_labor",
        store=True
    )

    iv_survey_schedule = fields.Selection(string="Survey Schedule", related="active_event_hh_labor.survey_sched")
    iv_no_hh_members_women = fields.Integer(
        "Number of Women in the Household", related="active_event_hh_labor.no_hh_members_women"
    )
    iv_no_hh_members_men = fields.Integer(
        "Number of Men in the Household", related="active_event_hh_labor.no_hh_members_men"
    )
    iv_no_hh_members = fields.Integer(
        "Total Number of Household Members", related="active_event_hh_labor.no_hh_members"
    )

    iv_hh_labor_availability_15_35_women = fields.Integer(
        "Number of women labors in the household between 15 - 35 years old",
        related="active_event_hh_labor.hh_labor_availability_15_35_women",
    )
    iv_hh_labor_availability_15_35_men = fields.Integer(
        "Number of men labors in the household between 15 - 35 years old",
        related="active_event_hh_labor.hh_labor_availability_15_35_men",
    )
    iv_tot_hh_labor_availability_15_35 = fields.Integer(
        "Total number of labors in the household between 15 - 35 years old",
        related="active_event_hh_labor.tot_hh_labor_availability_15_35",
    )

    iv_hh_labor_availability_36_60_women = fields.Integer(
        "Number of women labors in the household between 36 - 60 years old",
        related="active_event_hh_labor.hh_labor_availability_36_60_women",
    )
    iv_hh_labor_availability_36_60_men = fields.Integer(
        "Number of men labors in the household between 36 - 60 years old",
        related="active_event_hh_labor.hh_labor_availability_36_60_men",
    )
    iv_tot_hh_labor_availability_36_60 = fields.Integer(
        "Total number of labors in the household between 36 - 60 years old",
        related="active_event_hh_labor.tot_hh_labor_availability_36_60",
    )

    iv_labor_availability_agri_15_35_women = fields.Integer(
        "Number of women labors in the household, between 15 - 35 years old, availability in agriculture",
        related="active_event_hh_labor.labor_availability_agri_15_35_women",
    )
    iv_labor_availability_agri_15_35_men = fields.Integer(
        "Number of men labors in the household, between 15 - 35 years old, availability in agriculture",
        related="active_event_hh_labor.labor_availability_agri_15_35_men",
    )
    iv_tot_labor_availablity_agri_15_35 = fields.Integer(
        "Total number of labors in the household, between 15 - 35 years old, availability in agriculture",
        related="active_event_hh_labor.tot_labor_availablity_agri_15_35",
    )

    iv_labor_availability_agri_36_60_women = fields.Integer(
        "Number of women labors in the household, between 36 - 60 years old, availability in agriculture",
        related="active_event_hh_labor.labor_availability_agri_36_60_women",
    )
    iv_labor_availability_agri_36_60_men = fields.Integer(
        "Number of men labors in the household, between 36 - 60 years old, availability in agriculture",
        related="active_event_hh_labor.labor_availability_agri_36_60_men",
    )
    iv_tot_labor_availablity_agri_36_60 = fields.Integer(
        "Total number of labors in the household, between 36 - 60 years old, availability in agriculture",
        related="active_event_hh_labor.tot_labor_availablity_agri_36_60",
    )

    @api.depends("event_data_ids")
    def _compute_active_event_hh_labor(self):
        """
        This computes the active Household Member and Labor Availability event of the group
        """
        for rec in self:
            event_data = rec._get_active_event_id("spp.event.hh.labor")
            rec.active_event_hh_labor = None
            if event_data:
                event_data_res_id = self.env["spp.event.data"].search([("id", "=", event_data)], limit=1).res_id
                rec.active_event_hh_labor = (
                    self.env["spp.event.hh.labor"].search([("id", "=", event_data_res_id)], limit=1).id
                )
