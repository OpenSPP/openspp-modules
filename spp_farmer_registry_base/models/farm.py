from odoo import fields, models


class Farm(models.Model):
    _inherit = "res.partner"

    coordinates = fields.Char(string="GPS Coordinates")
