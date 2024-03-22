# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import Command, _, fields, models

_logger = logging.getLogger(__name__)


class SPPCycle(models.Model):
    _inherit = "g2p.cycle"

    is_manual_entitlement = fields.Boolean(compute="_compute_is_manual_entitlement")

    def _compute_is_manual_entitlement(self):
        for rec in self:
            is_manual_entitlement = False
            curr_entitlement_manager = self.env["g2p.program.entitlement.manager.default"].search(
                [("program_id", "=", rec.program_id.id), ("is_manual_cash", "=", True)]
            )
            if curr_entitlement_manager:
                is_manual_entitlement = True

            rec.is_manual_entitlement = is_manual_entitlement

    def search_existing_entitlement(self, registrant):
        current_entitlement = self.env["g2p.entitlement"].search(
            [("partner_id", "=", registrant), ("cycle_id", "=", self.id)]
        )
        if current_entitlement:
            return True
        return False

    def prepare_entitlement_manual(self):
        view = self.env.ref("spp_manual_entitlement.manual_entitlement_wizard_form_view")

        cycle_memberships = self.cycle_membership_ids.mapped("partner_id.id")
        cycle_membership_vals = []
        for cycle_member in cycle_memberships:
            with_existing_entitlement = self.search_existing_entitlement(cycle_member)
            if not with_existing_entitlement:
                vals = {"partner_id": cycle_member}
                cycle_membership_vals.append(Command.create(vals))

        wiz = self.env["spp.manual.entitlement.wizard"].create(
            {"cycle_id": self.id, "cycle_membership_ids": cycle_membership_vals, "step": "step1"}
        )

        return {
            "name": _("Manual Entitlement"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "spp.manual.entitlement.wizard",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "res_id": wiz.id,
            "context": self.env.context,
        }
