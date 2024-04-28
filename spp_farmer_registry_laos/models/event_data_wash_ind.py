from odoo import api, fields, models


class OpenSPPEventDataWashIndicators(models.Model):
    _name = "spp.event.wash.ind"
    _description = "XV. WASH Indicators"

    survey_sched = fields.Selection(
        [("1", "Baseline"), ("2", "Midline"), ("3", "Endline")],
        string="Survey Schedule",
    )
    water_sources = fields.Selection(
        [
            ("1", "Safety Managed"),
            ("2", "Basic"),
            ("3", "Limited"),
            ("4", "Unimproved"),
            ("5", "Surface Water"),
        ]
    )
    latrine_condition = fields.Selection(
        [
            ("1", "Safety Managed"),
            ("2", "Basic"),
            ("3", "Limited"),
            ("4", "Unimproved"),
            ("5", "Open Defecation"),
        ]
    )
    handwashing_facility = fields.Selection(
        [
            ("1", "Basic"),
            ("2", "Limited"),
            ("3", "No Facility"),
        ]
    )

    def get_view_id(self):
        """
        This retrieves the View ID of this model
        """
        return self.env["ir.ui.view"].search([("model", "=", self._name), ("type", "=", "form")], limit=1).id


class OpenSPPEventDataWashIndicatorsResPartner(models.Model):
    _inherit = "res.partner"

    active_event_wash_ind = fields.Many2one(
        "spp.event.wash.ind",
        compute="_compute_active_event_wash_ind",
        store=True
    )

    xv_survey_schedule = fields.Selection(string="Survey Schedule", related="active_event_wash_ind.survey_sched")
    xv_water_sources = fields.Selection(string="Water Sources", related="active_event_wash_ind.water_sources")
    xv_latrine_condition = fields.Selection(
        string="Latrine Condition", related="active_event_wash_ind.latrine_condition"
    )
    xv_handwashing_facility = fields.Selection(
        string="Hand-washing Facility", related="active_event_wash_ind.handwashing_facility"
    )

    @api.depends("event_data_ids")
    def _compute_active_event_wash_ind(self):
        """
        This computes the active WASH Indicators event of the group
        """
        for rec in self:
            event_data = rec._get_active_event_id("spp.event.wash.ind")
            rec.active_event_wash_ind = None
            if event_data:
                event_data_res_id = self.env["spp.event.data"].search([("id", "=", event_data)], limit=1).res_id
                rec.active_event_wash_ind = (
                    self.env["spp.event.wash.ind"].search([("id", "=", event_data_res_id)], limit=1).id
                )
