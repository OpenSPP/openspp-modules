import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SPPResPartner(models.Model):
    _inherit = "res.partner"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=False,
    )

    @api.onchange("phone_number_ids")
    def phone_number_ids_change(self):
        phone = ""
        if self.phone_number_ids:
            phone = ", ".join(
                [p for p in self.phone_number_ids.filtered(lambda rec: not rec.disabled).mapped("phone_no")]
            )
        self.phone = phone
