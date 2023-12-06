# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SPPEntitlement(models.Model):
    _inherit = "g2p.entitlement"

    state = fields.Selection(
        selection_add=[("parrdpd2ben", "Partially Redeemed/Paid to Beneficiary")]
    )
    transaction_ids = fields.One2many(
        "spp.entitlement.transactions", "entitlement_id", "Transactions"
    )
    entitlement_balance = fields.Float(compute="_compute_balance")

    @api.depends("transaction_ids")
    def _compute_balance(self):
        for rec in self:
            total_add = 0
            total_deduct = 0
            for transaction in rec.transaction_ids:
                if transaction.transaction_type == "PURCHASE":
                    total_add += transaction.amount_charged_by_service_point
                elif transaction.transaction_type == "VOID":
                    total_deduct += transaction.amount_charged_by_service_point
            initial_balance = rec.initial_amount
            total_balance = initial_balance - (total_add - total_deduct)
            rec.entitlement_balance = total_balance
