# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging
import random
from datetime import date

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class OpenSPPRequestIDWizard(models.TransientModel):
    _name = "spp.request.id.wizard"
    _description = "Request ID Wizard"

    registrant_id = fields.Many2one("res.partner", "Registrant ID", required=True)
    id_type = fields.Many2one("g2p.id.type")
    is_pds = fields.Boolean(default=False)
    is_idpass = fields.Boolean(default=False)
    target_type = fields.Char(compute="_compute_target_type")
    idpass_id = fields.Many2one(
        "spp.id.pass", "IDPass ID", domain="[('id_type', '=', id_type)]"
    )
    mii = fields.Char("MII", default="9")
    iin = fields.Char("IIN", default="0000")
    acc_number = fields.Char("Account Number", compute="_compute_acc_number")
    pds_number = fields.Char("PDS Card Number")

    @api.depends("registrant_id")
    def _compute_target_type(self):
        for rec in self:
            if rec.registrant_id:
                if rec.registrant_id.is_group:
                    rec.target_type = "group"
                else:
                    rec.target_type = "individual"

    @api.depends("mii", "iin")
    def _compute_acc_number(self):
        for rec in self:
            random_acc_number = random.randint(1, 9999999999)
            rec.acc_number = str(random_acc_number).zfill(10)
            pds_number = ""
            if rec.mii:
                pds_number = rec.mii
            if rec.iin:
                pds_number += rec.iin
            if rec.acc_number:
                pds_number += rec.acc_number

            has_existing_pds = self.env["g2p.reg.id"].search(
                [
                    ("id_type", "=", self.env.ref("spp_idpass.id_type_pds_number").id),
                    ("value", "=", pds_number),
                ]
            )
            if not has_existing_pds:
                rec.pds_number = pds_number
            else:
                rec._compute_acc_number()

    def request_id(self):
        for rec in self:
            if rec.id_type:
                params = self.env["ir.config_parameter"].sudo()
                auto_approve_id_request = params.get_param(
                    "spp_id_queue.auto_approve_id_request"
                )
                status = "new"
                if auto_approve_id_request:
                    status = "approved"

                vals = {
                    "id_type": rec.id_type.id,
                    "idpass_id": rec.idpass_id.id or False,
                    "requested_by": self.env.user.id,
                    "date_requested": date.today(),
                    "status": status,
                    "registrant_id": rec.registrant_id.id,
                }

                if rec.is_pds and rec.pds_number:
                    vals.update({"pds_number": rec.pds_number})

                self.env["spp.id.queue"].create(vals)
            else:
                raise UserError(_("There are no selected Template!"))

    @api.onchange("id_type")
    def _onchange_template(self):
        for rec in self:
            rec.is_idpass = False
            rec.is_pds = False
            if (
                rec.id_type
                and rec.id_type.id == self.env.ref("spp_idpass.id_type_idpass").id
                or rec.id_type.id == self.env.ref("spp_idpass.id_type_pds_number").id
            ):
                rec.is_idpass = True

            if rec.id_type.id == self.env.ref("spp_idpass.id_type_pds_number").id:
                rec.is_pds = True
