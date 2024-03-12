from odoo import api, fields, models


class FarmActivity(models.Model):
    _inherit = "spp.farm.activity"

    product_id = fields.Integer("Product ID")
    product_name = fields.Char("Product Name")
    product_name_eng = fields.Char("Product Name (English)")
    prod_farm_id = fields.Many2one("res.partner", string="Product Farm")

