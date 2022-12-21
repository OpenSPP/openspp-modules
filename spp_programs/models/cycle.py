# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models

from . import constants


class G2PCycle(models.Model):
    _inherit = "g2p.cycle"

    STATE_DRAFT = constants.STATE_DRAFT
    STATE_TO_APPROVE = constants.STATE_TO_APPROVE
    STATE_APPROVED = constants.STATE_APPROVED
    STATE_CANCELED = constants.STATE_CANCELLED
    STATE_DISTRIBUTED = constants.STATE_DISTRIBUTED
    STATE_ENDED = constants.STATE_ENDED

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

    def approve(self):
        # 1. Make sure the user has the right to do this
        # 2. Approve the cycle using the cycle manager
        for rec in self:
            cycle_managers = self.program_id.get_manager(constants.MANAGER_CYCLE)

            auto_approve = False
            if cycle_managers.auto_approve_entitlements:
                auto_approve = True

            retval = None
            if auto_approve:
                entitlement_manager = self.program_id.get_manager(
                    constants.MANAGER_ENTITLEMENT
                )
                if entitlement_manager.IS_CASH_ENTITLEMENT:
                    entitlement_obj = self.env["g2p.entitlement"]
                else:
                    entitlement_obj = self.env["g2p.entitlement.inkind"]
                entitlements = entitlement_obj.search(
                    [
                        ("cycle_id", "=", rec.id),
                        ("state", "=", "draft"),
                    ]
                )
                if entitlements:
                    retval = entitlements.approve_entitlement()

            if rec.state == self.STATE_TO_APPROVE:
                rec.update({"state": self.STATE_APPROVED})
                # Running on_state_change because it is not triggered automatically with rec.update above
                rec.on_state_change()
                return retval
            else:
                message = _("Only 'to approve' cycles can be approved.")
                kind = "danger"

                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Cycle"),
                        "message": message,
                        "sticky": True,
                        "type": kind,
                        "next": {
                            "type": "ir.actions.act_window_close",
                        },
                    },
                }
