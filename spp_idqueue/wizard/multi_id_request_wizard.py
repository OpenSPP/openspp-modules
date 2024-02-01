# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging
from datetime import date

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class OpenSPPMultiIDRequestWizard(models.TransientModel):
    _name = "spp.multi.id.request.wizard"
    _description = "Multiple ID Request Wizard"

    @api.model
    def default_get(self, fields):
        """
        Default Get
        These overrides the default_get function to set the
        registrant_ids base on the selected registrants 'active_ids'
        """
        res = super().default_get(fields)
        if self.env.context.get("active_ids"):
            registrant_ids = self.env["res.partner"].search([("id", "in", self.env.context.get("active_ids"))])
            if registrant_ids:
                res["registrant_ids"] = registrant_ids
            return res
        else:
            raise UserError(_("There are no selected Registrants!"))

    registrant_ids = fields.Many2many("res.partner")
    id_type = fields.Many2one("g2p.id.type")
    is_idpass = fields.Boolean(default=False)
    idpass_id = fields.Many2one("spp.id.pass", "IDPass ID", domain="[('id_type', '=', id_type)]")
    target_type = fields.Char(compute="_compute_target_type")

    @api.depends("registrant_ids")
    def _compute_target_type(self):
        """
        This function is used to compute the target_type
        """
        for rec in self:
            if not rec.registrant_ids:
                raise UserError(_("There are no selected Registrants!"))
            if rec.registrant_ids[0].is_group:
                rec.target_type = "group"
            else:
                rec.target_type = "individual"

    @api.onchange("id_type")
    def _onchange_template(self):
        """
        This function is used to set is_idpass on Template Onchange
        """
        for rec in self:
            rec.is_idpass = False
            if rec.id_type and rec.id_type.id == self.env.ref("spp_idpass.id_type_idpass").id:
                rec.is_idpass = True

    def create_requests(self):
        """
        This function is used to create the request or requests
        """
        for rec in self:
            if rec.id_type:
                if rec.registrant_ids:
                    params = self.env["ir.config_parameter"].sudo()
                    auto_approve_id_request = params.get_param("spp_id_queue.auto_approve_id_request")
                    status = "new"
                    if auto_approve_id_request:
                        status = "approved"
                    counter = 0
                    for registrant in rec.registrant_ids:
                        vals = {
                            "id_type": rec.id_type.id,
                            "idpass_id": rec.idpass_id.id or False,
                            "requested_by": self.env.user.id,
                            "date_requested": date.today(),
                            "status": status,
                            "registrant_id": registrant.id,
                        }

                        self.env["spp.print.queue.id"].create(vals)
                        counter += 1

                    message = _("%s request(s) created.", counter)
                    kind = "info"
                    return {
                        "type": "ir.actions.client",
                        "tag": "display_notification",
                        "params": {
                            "title": _("ID Requests"),
                            "message": message,
                            "sticky": True,
                            "type": kind,
                            "next": {
                                "type": "ir.actions.act_window_close",
                            },
                        },
                    }
            else:
                raise UserError(_("There are no selected Template!"))
        return

    def open_wizard(self):
        return {
            "name": "Create Multiple ID Request",
            "view_mode": "form",
            "res_model": self._name,
            "view_id": self.env.ref("spp_idqueue.multi_id_request_wizard_form_view").id,
            "type": "ir.actions.act_window",
            "target": "new",
            "context": self.env.context,
        }
