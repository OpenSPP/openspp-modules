# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class G2PCycle(models.Model):
    _inherit = "g2p.cycle"

    # STATE_DRAFT = constants.STATE_DRAFT
    # STATE_TO_APPROVE = constants.STATE_TO_APPROVE
    # STATE_APPROVED = constants.STATE_APPROVED
    # STATE_CANCELED = constants.STATE_CANCELLED
    # STATE_DISTRIBUTED = constants.STATE_DISTRIBUTED
    # STATE_ENDED = constants.STATE_ENDED

    inkind_entitlement_ids = fields.One2many(
        "g2p.entitlement.inkind", "cycle_id", "In-Kind Entitlements"
    )
    inkind_entitlements_count = fields.Integer(
        string="# In-kind Entitlements",
        compute="_compute_inkind_entitlements_count",
        store=True,
    )

    # Stock Management Fields
    picking_ids = fields.One2many("stock.picking", "cycle_id", string="Stock Transfers")
    procurement_group_id = fields.Many2one("procurement.group", "Procurement Group")

    @api.depends("inkind_entitlement_ids")
    def _compute_inkind_entitlements_count(self):
        for rec in self:
            entitlements_count = 0
            if rec.inkind_entitlement_ids:
                entitlements_count = len(rec.inkind_entitlement_ids)
            rec.update({"inkind_entitlements_count": entitlements_count})
