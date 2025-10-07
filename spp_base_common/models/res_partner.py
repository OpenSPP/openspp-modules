import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class SPPResPartner(models.Model):
    _inherit = "res.partner"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=False,
    )
