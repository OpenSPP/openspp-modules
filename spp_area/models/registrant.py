# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class G2PRegistrant(models.Model):
    _inherit = "res.partner"

    # Custom Fields
    area_id = fields.Many2one(
        "spp.area", "Area", domain="[('kind', '=', 'Home Address')]"
    )
