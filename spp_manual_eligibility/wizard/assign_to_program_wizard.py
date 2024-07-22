# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class G2PAssignToProgramWizard(models.TransientModel):
    _inherit = "g2p.assign.program.wizard"

    def assign_registrant(self):
        vals = super().assign_registrant()
        for rec in self:
            if rec.program_id and rec.program_id.is_manual_eligibility:
                for beneficiary in rec.program_id.program_membership_ids:
                    if not beneficiary.state == "enrolled":
                        beneficiary.write(
                            {
                                "state": "enrolled",
                                "enrollment_date": fields.Datetime.now(),
                            }
                        )
        return vals
