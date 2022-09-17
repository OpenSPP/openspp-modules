# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class OpenSPPSetPinWizard(models.TransientModel):
    _name = "spp.set.pin.wizard"
    _description = "Set Pin Wizard"

    pin_code = fields.Char()
    pin_code_confirm = fields.Char("Confirm Pin Code")
    registrant_id = fields.Many2one("res.partner", "Registrant ID", readonly=True)
    reg_id = fields.Many2one("g2p.reg.id", "PDS ID Document", readonly=True)
    reg_id_pds = fields.Char(related="reg_id.value")

    def set_pin(self):
        for rec in self:
            if rec.pin_code == rec.pin_code_confirm:
                vals = {"pin_code": rec.pin_code}
                rec.reg_id.write(vals)
            else:
                raise UserError(_("Pin Code doesn't Match!"))

    @api.onchange("pin_code")
    def _onchange_pin_code(self):
        for rec in self:
            if len(rec.pin_code) > 6:
                raise UserError(_("Only 6 digits are allowed"))

            for char in rec.pin_code:
                if char.isalpha():
                    raise UserError(_("Only digits are allowed"))
