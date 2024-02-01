# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class G2PBasicEntitlementCashSpent(models.Model):
    _inherit = "g2p.entitlement"

    spent_amount = fields.Monetary(required=True, currency_field="currency_id", default=0.0)

    def _compute_balance(self):
        for rec in self:
            rec.balance = rec.initial_amount - rec.spent_amount
