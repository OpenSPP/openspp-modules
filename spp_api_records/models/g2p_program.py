from odoo import fields, models


class G2PPrograms(models.Model):
    _inherit = "g2p.program"

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
