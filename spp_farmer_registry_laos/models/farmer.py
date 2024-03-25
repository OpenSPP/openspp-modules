import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class Farmer(models.Model):
    _inherit = "res.partner"

    marital_status = fields.Selection(
        selection_add=[
            ("married_monogamous", "Married Monogamous"),
            ("married_polygamous", "Married Polygamous"),
        ]
    )


class TempFarmer(models.Model):
    _inherit = "spp.farmer"

    farmer_marital_status = fields.Selection(
        selection_add=[
            ("married_monogamous", "Married Monogamous"),
            ("married_polygamous", "Married Polygamous"),
        ]
    )
