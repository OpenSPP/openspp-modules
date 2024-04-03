from odoo import fields, models


class OpenSPPEventDataWashIndicators(models.Model):
    _name = "spp.event.wash.ind"
    _description = "WASH Indicators"

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
