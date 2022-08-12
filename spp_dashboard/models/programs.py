# Part of Newlogic OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import _, fields, models

_logger = logging.getLogger(__name__)


class G2PProgram(models.Model):
    _inherit = "g2p.program"

    dashboard_id = fields.Many2one(
        "dashboard.menu",
        "Dashboard",
        default=lambda self: self.env.ref("spp_dashboard.dashboard_menu_program")
        or None,
    )

    # Statistics Functions
    def count_beneficiaries(self, state=None):
        company_id = self.env.user.company_id and self.env.user.company_id.id or None
        domain = []
        if company_id:
            domain = [("program_id.company_id", "=", company_id)]

        if state is not None:
            domain += [("state", "in", state)]
        _logger.info("DEBUG! %s" % domain)
        return {"value": self.env["g2p.program_membership"].search_count(domain)}

    def open_dashboard(self):
        self.ensure_one()

        if self.dashboard_id:
            action = self.dashboard_id.client_action
            return {
                "type": "ir.actions.client",
                "name": action.name,
                "tag": action.tag,
                "id": action.id,
                # 'context': {'record_id':self.id},
            }

        else:
            message = _("A dashboard must be defined for this program.")
            kind = "danger"

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Program"),
                    "message": message,
                    "sticky": True,
                    "type": kind,
                },
            }
