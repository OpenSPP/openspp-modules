# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, fields, models

_logger = logging.getLogger(__name__)


class OpenSPPRegistrant(models.Model):
    _inherit = "res.partner"

    id_requests = fields.One2many("spp.print.queue.id", "registrant_id", string="ID Requests")

    def open_request_id_wizard(self):
        view = self.env.ref("spp_idqueue.request_id_wizard_form_view")
        wiz = self.env["spp.print.queue.wizard"].create({"registrant_id": self.id})
        return {
            "name": _("Request ID"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "spp.print.queue.wizard",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "res_id": wiz.id,
            "context": self.env.context,
        }
