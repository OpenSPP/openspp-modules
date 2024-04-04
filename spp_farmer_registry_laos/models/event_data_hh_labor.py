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
