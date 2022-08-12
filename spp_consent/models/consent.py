# Part of Newlogic OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class OpenSPPConsent(models.Model):
    _name = "spp.consent"
    _description = "OpenSPP Consent"

    name = fields.Char("Consent", required=True)
    signatory_id = fields.Many2one(
        "res.partner", "Individual", domain=[("is_group", "=", False)]
    )
    expiry = fields.Date("Expiry Date", required=True)
    config_id = fields.Many2one("spp.consent.config", "Config")
