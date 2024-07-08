# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
import logging

from odoo import fields, models

# from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class G2PCreateNewProgramWiz(models.TransientModel):
    _inherit = "g2p.program.create.wizard"

    eligibility_kind = fields.Selection(selection_add=[("manual_eligibility", "Manual Eligibility")])

    def _get_default_eligibility_manager_val(self, program_id):
        val = super()._get_default_eligibility_manager_val(program_id)
        is_manual_eligibility = False
        eligibility_domain = self.eligibility_domain
        eligibility_name = "Default"
        for rec in self:
            if rec.eligibility_kind == "manual_eligibility":
                is_manual_eligibility = True
                eligibility_domain = None
                eligibility_name = "Manual Eligibility"
        val.update(
            {
                "name": eligibility_name,
                "eligibility_domain": eligibility_domain,
                "is_manual_eligibility": is_manual_eligibility,
            }
        )

        return val

    def _get_eligibility_manager(self, program_id):
        val = super()._get_eligibility_manager(program_id)
        if self.eligibility_kind == "manual_eligibility":
            # Add a new record to default eligibility manager model
            default_eligibility_manager_val = self._get_default_eligibility_manager_val(program_id)
            def_mgr = self.env["g2p.program_membership.manager.default"].create(default_eligibility_manager_val)

            # Add a new record to eligibility manager parent model
            eligibility_manager_val = self._get_eligibility_managers_val(program_id, def_mgr)
            mgr = self.env["g2p.eligibility.manager"].create(eligibility_manager_val)

            val = {"eligibility_managers": [(4, mgr.id)]}
        return val
