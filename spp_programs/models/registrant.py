# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class G2PRegistrantCustom(models.Model):
    _inherit = "res.partner"

    # Custom Fields
    inkind_entitlement_ids = fields.One2many("g2p.entitlement.inkind", "partner_id", "In-kind Entitlements")

    # Statistics
    inkind_entitlements_count = fields.Integer(
        string="# In-kind Entitlements",
        compute="_compute_inkind_entitlements_count",
        store=True,
    )

    @api.depends("inkind_entitlement_ids")
    def _compute_inkind_entitlements_count(self):
        for rec in self:
            inkind_entitlements_count = self.env["g2p.entitlement.inkind"].search_count([("partner_id", "=", rec.id)])
            rec.update({"inkind_entitlements_count": inkind_entitlements_count})
