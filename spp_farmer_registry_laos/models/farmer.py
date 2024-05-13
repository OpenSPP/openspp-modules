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
    geo_img_file = fields.Binary(string="Geometry Image File")
    geo_img_file_filename = fields.Char(string="File Name")


class TempFarmer(models.Model):
    _inherit = "spp.farmer"

    farmer_marital_status = fields.Selection(
        selection_add=[
            ("married_monogamous", "Married Monogamous"),
            ("married_polygamous", "Married Polygamous"),
        ]
    )
