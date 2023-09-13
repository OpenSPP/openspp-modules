# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import models

from odoo.addons.g2p_programs.models import constants


class SPPDefaultCycleManager(models.Model):
    _inherit = "g2p.cycle.manager.default"

    def mark_ended(self, cycle):
        self.check_cycle_entitlements(cycle)
        cycle.update({"state": constants.STATE_ENDED})

    def check_cycle_entitlements(self, cycle):
        for entitlement in cycle.entitlement_ids:
            state = self.check_entitlements_transactions(entitlement)
            entitlement.update({"state": state})

    def check_entitlements_transactions(self, entitlement):
        total_purchase = 0
        total_void = 0
        state = entitlement.state

        if entitlement.transaction_ids:
            state = "parrdpd2ben"

        for transactions in entitlement.transaction_ids:

            if transactions.transaction_type == "PURCHASE":
                total_purchase += transactions.amount_charged_by_service_point

            elif transactions.transaction_type == "VOID":
                total_void += transactions.amount_charged_by_service_point

        total_amount = total_purchase - total_void

        if total_amount == entitlement.initial_amount:
            state = "rdpd2ben"

        return state
