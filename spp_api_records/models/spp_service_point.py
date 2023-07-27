from odoo import fields, models


class SppServicePoint(models.Model):
    _inherit = "spp.service.point"

    topup_service_point = fields.Boolean(
        string="Allow Topup",
        help="Is service point where beneficiaries can go and top-up "
        "their cards to purchase commodities",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
