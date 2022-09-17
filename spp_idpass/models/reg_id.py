# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models


class OpenG2PRegId(models.Model):
    _inherit = "g2p.reg.id"

    pin_code = fields.Char("ID File Name")
    is_pds = fields.Boolean(default=False)

    def open_set_pin_wiz(self):
        view = self.env.ref("spp_idpass.set_pin_wizard_form_view")
        wiz = self.env["spp.set.pin.wizard"].create(
            {"registrant_id": self.partner_id.id, "reg_id": self.id}
        )
        return {
            "name": _("Set PIN"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "spp.set.pin.wizard",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "res_id": wiz.id,
            "context": self.env.context,
        }
