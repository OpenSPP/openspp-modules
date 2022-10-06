# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from datetime import date

from odoo import _, fields, models


class OpenSPPRegistrant(models.Model):
    _inherit = "res.partner"

    event_data_ids = fields.One2many("spp.event.data", "registrar", "Event Data IDs")

    def _compute_active_event(self, model):
        active_event = self.env["spp.event.data"].search(
            [
                ("registrar", "=", self.id),
                ("model", "=", model),
                ("expiry_date", "=", False),
            ]
        )
        active_event_id = None
        if active_event:
            active_event_id = active_event[0].id
        return active_event_id

    def end_active_event(self, res_id):
        if res_id:
            res_id.expiry_date = date.today()

    def open_create_event_wizard(self):
        for rec in self:
            view = self.env.ref("spp_event_data.create_event_data_form_view")
            wiz = self.env["spp.create.event.wizard"].create({"registrant": rec.id})
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
