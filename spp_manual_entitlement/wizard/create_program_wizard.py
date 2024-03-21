# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
import logging

from odoo import fields, models

# from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class G2PCreateNewProgramWiz(models.TransientModel):
    _inherit = "g2p.program.create.wizard"

    entitlement_kind = fields.Selection(selection_add=[("manual_cash", "Manual Cash")])

    def _get_entitlement_manager(self, program_id):
        val = None
        def_mgr_obj = "g2p.program.entitlement.manager.default"
        def_mgr = None
        if self.entitlement_kind == "default":
            # Add a new record to default entitlement manager model
            def_mgr = self.env[def_mgr_obj].create(
                {
                    "name": "Default",
                    "program_id": program_id,
                    "amount_per_cycle": self.amount_per_cycle,
                    "amount_per_individual_in_group": self.amount_per_individual_in_group,
                    "transfer_fee_pct": self.transfer_fee_pct,
                    "transfer_fee_amt": self.transfer_fee_amt,
                    "max_individual_in_group": self.max_individual_in_group,
                    "entitlement_validation_group_id": self.entitlement_validation_group_id.id,
                }
            )
        elif self.entitlement_kind == "manual_cash":
            def_mgr = self.env[def_mgr_obj].create(
                {
                    "name": "Manual Cash",
                    "program_id": program_id,
                    "is_manual_cash": True,
                    "entitlement_validation_group_id": self.entitlement_validation_group_id.id,
                }
            )

        if def_mgr:
            # Add a new record to entitlement manager parent model
            man_obj = self.env["g2p.program.entitlement.manager"]
            mgr = man_obj.create(
                {
                    "program_id": program_id,
                    "manager_ref_id": f"{def_mgr_obj},{str(def_mgr.id)}",
                }
            )
            val = {"entitlement_managers": [(4, mgr.id)]}

            return val
