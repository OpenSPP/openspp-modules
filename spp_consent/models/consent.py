# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class OpenSPPConsent(models.Model):
    _name = "spp.consent"
    _description = "OpenSPP Consent"

    name = fields.Char("Consent", required=True)
    group_id = fields.Many2one(
        "res.partner",
        "Group",
        domain=[("is_registrant", "=", True), ("is_group", "=", True)],
    )
    signatory_id = fields.Many2one(
        "res.partner",
        "Signatory",
        domain=[("is_registrant", "=", True), ("is_group", "=", False)],
    )
    expiry = fields.Date("Expiry Date", required=True)
    config_id = fields.Many2one("spp.consent.config", "Config")
