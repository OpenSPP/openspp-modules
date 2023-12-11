# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from datetime import date

from odoo import fields, models

from odoo.addons.g2p_programs.models import constants


class SPPCycle(models.Model):
    _inherit = "g2p.cycle"

    is_expired = fields.Boolean(compute="_compute_is_expired")

    def _compute_is_expired(self):
        for rec in self:
            is_expired = False
            if rec.end_date <= date.today():
                is_expired = True

            rec.is_expired = is_expired


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
        balance = entitlement.entitlement_balance
        initial_amount = entitlement.initial_amount
        state = entitlement.state

        if initial_amount > balance:
            state = "parrdpd2ben"
        elif initial_amount == balance:
            state = entitlement.state

        if balance == 0:
            state = "rdpd2ben"

        return state
