# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class G2PRegistrant(models.Model):
    _inherit = "res.partner"

    @api.model
    def _get_area_domain(self):
        area_id = self.env.ref("spp_area.admin_area_kind").id
        return [("kind", "=", area_id)]

    # Custom Fields
    area_id = fields.Many2one(
        "spp.area",
        "Area",
        domain=_get_area_domain,
    )
