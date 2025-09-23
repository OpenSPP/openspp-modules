from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_donor = fields.Boolean(
        string="Is Donor",
        help="Check if this partner is a donor",
        tracking=True,
        index=True,
    )
