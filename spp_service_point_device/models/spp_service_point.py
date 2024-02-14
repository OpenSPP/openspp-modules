from odoo import _, fields, models


class SppServicePoint(models.Model):
    _inherit = "spp.service.point"

    topup_service_point = fields.Boolean(
        string="Allow Topup",
        help="Is service point where beneficiaries can go and top-up " "their cards to purchase commodities",
    )

    def action_view_terminal_devices(self):
        self.ensure_one()
        return {
            "name": _("Terminal Devices"),
            "type": "ir.actions.act_window",
            "res_model": "spp.service.point.device",
            "view_mode": "tree,form",
            "domain": [("service_point_id", "=", self.id)],
            "context": dict(
                self._context,
                create=False,
                edit=False,
                delete=False,
                default_service_point_id=self.id,
            ),
        }
