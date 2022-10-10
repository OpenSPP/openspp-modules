# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


from odoo import _, fields, models


class OpenSPPRegistrant(models.Model):
    _inherit = "res.partner"

    event_data_ids = fields.One2many("spp.event.data", "partner_id", "Event Data IDs")

    def open_create_event_wizard(self):
        for rec in self:
            view = self.env.ref("spp_event_data.create_event_data_form_view")
            wiz = self.env["spp.create.event.wizard"].create({"partner_id": rec.id})
            return {
                "name": _("Create Event Wizard"),
                "view_mode": "form",
                "res_model": "spp.create.event.wizard",
                "res_id": wiz.id,
                "view_id": view.id,
                "type": "ir.actions.act_window",
                "target": "new",
                "context": self.env.context,
            }
