# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class G2PProgram(models.Model):
    _inherit = "g2p.program"

    is_manual_eligibility = fields.Boolean(compute="_compute_is_manual_eligibility")

    def _compute_is_manual_eligibility(self):
        for rec in self:
            is_manual_eligibility = False
            curr_eligibility_manager = self.env["g2p.program_membership.manager.default"].search(
                [("program_id", "=", rec.id), ("is_manual_eligibility", "=", True)]
            )
            if curr_eligibility_manager:
                is_manual_eligibility = True

            rec.is_manual_eligibility = is_manual_eligibility
