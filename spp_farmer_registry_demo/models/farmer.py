from odoo import fields, models


class Farmer(models.Model):
    _inherit = "res.partner"

    marital_status = fields.Selection(
        [
            ("single", "Single"),
            ("married_monogamous", "Married Monogamous"),
            ("married_polygamous", "Married Polygamous"),
            ("widowed", "Widowed"),
            ("separated", "Separated"),
        ],
    )
    highest_education_level = fields.Selection(
        [
            ("none", "None"),
            ("primary", "Primary"),
            ("secondary", "Secondary"),
            ("certificate", "Certificate"),
            ("diploma", "Diploma"),
            ("university", "University"),
            ("tertiary", "Tertiary"),
        ],
    )
