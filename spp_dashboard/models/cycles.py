# Part of Newlogic OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models


class G2PCycle(models.Model):
    _inherit = "g2p.cycle"

    dashboard_id = fields.Many2one(
        "dashboard.menu",
        "Dashboard",
        default=lambda self: self.env.ref("spp_dashboard.dashboard_menu_cycle") or None,
    )

    def open_dashboard(self):
        self.ensure_one()

        if self.dashboard_id:
            action = self.dashboard_id.client_action
            return {
                "type": "ir.actions.client",
                "name": action.name,
                "tag": action.tag,
                "id": action.id,
            }

        else:
            message = _("A dashboard must be defined for this cycle.")
            kind = "danger"

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Cycle"),
                    "message": message,
                    "sticky": True,
                    "type": kind,
                },
            }
