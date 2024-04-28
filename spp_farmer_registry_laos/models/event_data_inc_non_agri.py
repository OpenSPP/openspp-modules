from odoo import api, fields, models


class OpenSPPEventDataIncomeFromNonAgriculture(models.Model):
    _name = "spp.event.inc.non.agri"
    _description = "XIV. Non-Agriculture Annual Income Sources (in LAK)"

    survey_sched = fields.Selection(
        [("1", "Baseline"), ("2", "Midline"), ("3", "Endline")],
        string="Survey Schedule",
    )
    salary = fields.Float("Income from Salary")
    wages = fields.Float("Income from Wages")
    handicraft = fields.Float("Income from Handicraft")
    ntfp = fields.Float("Income from NTFPs")
    remittance = fields.Float("Income from Remittance")
    business = fields.Float("Income from Business")
    land_lease = fields.Float("Income from Land Lease")
    other = fields.Float("Other Income from Non-Agriculture")
    total = fields.Float("Total Income from Non-Agriculture", compute="_compute_total")

    @api.depends("salary", "wages", "handicraft", "ntfp", "remittance", "business", "land_lease", "other")
    def _compute_total(self):
        for rec in self:
            rec.total = (
                rec.salary
                + rec.wages
                + rec.handicraft
                + rec.ntfp
                + rec.remittance
                + rec.business
                + rec.land_lease
                + rec.other
            )

    def get_view_id(self):
        """
        This retrieves the View ID of this model
        """
        return self.env["ir.ui.view"].search([("model", "=", self._name), ("type", "=", "form")], limit=1).id


class OpenSPPEventDataIncomeFromNonAgricultureResPartner(models.Model):
    _inherit = "res.partner"

    active_event_inc_non_agri = fields.Many2one(
        "spp.event.inc.non.agri",
        compute="_compute_active_event_inc_non_agri",
        store=True
    )

    xiv_survey_schedule = fields.Selection(string="Survey Schedule", related="active_event_inc_non_agri.survey_sched")
    xiv_salary = fields.Float("Income from Salary", related="active_event_inc_non_agri.salary")
    xiv_wages = fields.Float("Income from Wages", related="active_event_inc_non_agri.wages")
    xiv_handicraft = fields.Float("Income from Handicraft", related="active_event_inc_non_agri.handicraft")
    xiv_ntfp = fields.Float("Income from NTFPs", related="active_event_inc_non_agri.ntfp")
    xiv_remittance = fields.Float("Income from Remittance", related="active_event_inc_non_agri.remittance")
    xiv_business = fields.Float("Income from Business", related="active_event_inc_non_agri.business")
    xiv_land_lease = fields.Float("Income from Land Lease", related="active_event_inc_non_agri.land_lease")
    xiv_other = fields.Float("Other Income from Non-Agriculture", related="active_event_inc_non_agri.other")
    xiv_total = fields.Float("Total Income from Non-Agriculture", related="active_event_inc_non_agri.total")

    @api.depends("event_data_ids")
    def _compute_active_event_inc_non_agri(self):
        """
        This computes the active Non-Agriculture Annual Income Sources (in LAK) event of the group
        """
        for rec in self:
            event_data = rec._get_active_event_id("spp.event.inc.non.agri")
            rec.active_event_inc_non_agri = None
            if event_data:
                event_data_res_id = self.env["spp.event.data"].search([("id", "=", event_data)], limit=1).res_id
                rec.active_event_inc_non_agri = (
                    self.env["spp.event.inc.non.agri"].search([("id", "=", event_data_res_id)], limit=1).id
                )
