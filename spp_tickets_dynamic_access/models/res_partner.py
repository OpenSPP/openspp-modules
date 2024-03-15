from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    support_staff_ids = fields.Many2many(
        "res.users",
        "partner_support_staff_rel",  # This is the name of the relation table
        "partner_id",
        "user_id",
        string="Support Staff",
        help="Support staff who have dynamic access to this partner.",
    )
