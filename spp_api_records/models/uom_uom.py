from odoo import fields, models


class UomUom(models.Model):
    _inherit = "uom.uom"

    symbol = fields.Char(size=3)
