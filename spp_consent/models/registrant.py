# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import models


class OpenSPPRegistrant(models.Model):
    _name = "res.partner"
    _inherit = [_name, "spp.consent.mixin"]
