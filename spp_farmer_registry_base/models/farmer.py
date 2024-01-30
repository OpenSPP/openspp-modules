from odoo import fields, models


class Farmer(models.Model):
    _inherit = "res.partner"

    experience_years = fields.Integer(string="Years of Experience")
    formal_agricultural_training = fields.Integer()
