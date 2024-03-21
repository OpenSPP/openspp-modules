# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class DefaultCashEntitlementManager(models.Model):
    _inherit = "g2p.program.entitlement.manager.default"

    is_manual_cash = fields.Boolean(default=False)

    def manual_prepare_entitlements(self, cycle, beneficiaries):
        entitlement_start_validity = cycle.start_date
        entitlement_end_validity = cycle.end_date
        entitlement_currency = self.currency_id.id

        entitlements = []
        for beneficiary in beneficiaries:
            transfer_fee = 0.0
            if self.transfer_fee_pct > 0.0:
                transfer_fee = beneficiary.entitlement_amount * (self.transfer_fee_pct / 100.0)
            elif self.transfer_fee_amt > 0.0:
                transfer_fee = self.transfer_fee_amt
            entitlements.append(
                {
                    "cycle_id": cycle.id,
                    "partner_id": beneficiary.partner_id.id,
                    "initial_amount": beneficiary.entitlement_amount,
                    "transfer_fee": transfer_fee,
                    "currency_id": entitlement_currency,
                    "state": "draft",
                    "is_cash_entitlement": True,
                    "valid_from": entitlement_start_validity,
                    "valid_until": entitlement_end_validity,
                }
            )
        if entitlements:
            return self.env["g2p.entitlement"].create(entitlements)

        return None
