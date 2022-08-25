# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging
from datetime import date

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class OpenSPPRequestIDWizard(models.TransientModel):
    _name = "spp.request.id.wizard"
    _description = "Request ID Wizard"

    registrant_id = fields.Many2one("res.partner", "Registrant ID", required=True)
    template_id = fields.Many2one("g2p.id.type")
    is_idpass = fields.Boolean(default=False)
    idpass_id = fields.Many2one("spp.id.pass", "IDPass ID")

    def request_id(self):
        for rec in self:
            if rec.template_id:
                params = self.env["ir.config_parameter"].sudo()
                auto_approve_id_request = params.get_param(
                    "spp_id_queue.auto_approve_id_request"
                )
                status = "new"
                if auto_approve_id_request:
                    status = "approved"
                vals = {
                    "template_id": rec.template_id.id,
                    "idpass_id": rec.idpass_id.id or False,
                    "requested_by": self.env.user.id,
                    "date_requested": date.today(),
                    "status": status,
                    "registrant_id": rec.registrant_id.id,
                }
                self.env["spp.id.queue"].create(vals)
            else:
                raise UserError(_("There are no selected Template!"))

    @api.onchange("template_id")
    def _onchange_template(self):
        for rec in self:
            rec.is_idpass = False
            _logger.info(
                "ID REQUEST: %s %s"
                % (rec.template_id.id, self.env.ref("spp_idpass.id_type_idpass").id)
            )
            if (
                rec.template_id
                and rec.template_id.id == self.env.ref("spp_idpass.id_type_idpass").id
            ):
                rec.is_idpass = True
