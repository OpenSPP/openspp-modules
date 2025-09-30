from odoo import fields, models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "custom.filter.mixin"]

    program_membership_ids = fields.One2many(allow_filter=True)
