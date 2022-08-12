# Part of Newlogic OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class OpenSPPCreateConsentWizard(models.TransientModel):
    _name = "spp.create.consent.wizard"
    _description = "Create Consent Wizard"

    name = fields.Char("Consent")
    signatory_id = fields.Many2one(
        "res.partner", "Individual", domain=[("is_group", "=", False)]
    )
    expiry = fields.Date("Expiry Date")
    config_id = fields.Many2one("spp.consent.config", "Config")

    def create_consent(self):
        if self.signatory_id:
            vals = {
                "name": self.name,
                "signatory_id": self.signatory_id.id,
                "expiry": self.expiry,
                "config_id": self.config_id.id,
            }
            return self.signatory_id.write({"consent_ids": [(0, 0, vals)]})
        else:
            raise UserError(_("There are no selected Signatory!"))
