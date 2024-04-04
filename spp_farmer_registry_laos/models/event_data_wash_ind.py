from odoo import fields, models


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
