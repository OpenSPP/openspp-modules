# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class G2PCycle(models.Model):
    _inherit = "g2p.cycle"

    inkind_entitlement_ids = fields.One2many(
        "g2p.entitlement.inkind", "cycle_id", "In-Kind Entitlements"
    )
    inkind_entitlements_count = fields.Integer(
        string="# In-kind Entitlements",
    )

    # Stock Management Fields
    picking_ids = fields.One2many("stock.picking", "cycle_id", string="Stock Transfers")
    procurement_group_id = fields.Many2one("procurement.group", "Procurement Group")

    validate_async_err = fields.Boolean(default=False)

    def _compute_inkind_entitlements_count(self):
        for rec in self:
            entitlements_count = self.env["g2p.entitlement.inkind"].search_count(
                [("cycle_id", "=", rec.id)]
            )
            rec.update({"inkind_entitlements_count": entitlements_count})
