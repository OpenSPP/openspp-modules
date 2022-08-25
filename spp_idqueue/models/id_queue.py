# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from datetime import date

from odoo import api, fields, models


class OpenSPPIDQueue(models.Model):
    _name = "spp.id.queue"
    _description = "ID Queue"

    name = fields.Char("Request Name")
    template_id = fields.Many2one("g2p.id.type", required=True)
    idpass_id = fields.Many2one("spp.id.pass")
    requested_by = fields.Many2one("res.users", required=True)
    approved_by = fields.Many2one("res.users")
    printed_by = fields.Many2one("res.users")
    registrant_id = fields.Many2one("res.partner", required=True)
    date_requested = fields.Date()
    date_approved = fields.Date()
    date_printed = fields.Date()
    status = fields.Selection(
        [
            ("new", "New"),
            ("approved", "Approved"),
            ("printed", "Printed"),
            ("cancelled", "Cancelled"),
        ],
        default="new",
    )

    def approve(self):
        for rec in self:
            rec.date_approved = date.today()
            rec.approved_by = self.env.user.id
            rec.status = "approved"

    def print(self):
        for rec in self:
            if rec.template_id.id == self.env.ref("spp_idpass.id_type_idpass").id:
                vals = {"idpass": self.idpass_id.id}
                self.registrant_id.send_idpass_parameters(vals)

            rec.date_printed = date.today()
            rec.printed_by = self.env.user.id
            rec.status = "printed"

    def cancel(self):
        for rec in self:
            rec.status = "cancelled"


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    auto_approve_id_request = fields.Boolean(
        default=True,
        help="Check if you want to auto-approve ID requests",
        string="Auto-approve ID Requests",
    )

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env["ir.config_parameter"].set_param(
            "spp_id_queue.auto_approve_id_request", self.auto_approve_id_request
        )
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env["ir.config_parameter"].sudo()
        res.update(
            auto_approve_id_request=params.get_param(
                "spp_id_queue.auto_approve_id_request"
            )
        )
        return res
