from odoo import _, api, fields, models


class UomUom(models.Model):
    _inherit = "uom.uom"

    symbol = fields.Char(
        size=3
    )
