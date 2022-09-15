# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class OpenSPPConsentConfig(models.Model):
    _name = "spp.consent.config"
    _description = "OpenSPP Consent Config"

    name = fields.Char(required=True)
