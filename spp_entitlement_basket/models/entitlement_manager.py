# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class EntitlementManager(models.Model):
    _inherit = "g2p.program.entitlement.manager"

    @api.model
    def _selection_manager_ref_id(self):
        selection = super()._selection_manager_ref_id()
        new_manager = ("g2p.program.entitlement.manager.basket", "Entitlement Basket")
        if new_manager not in selection:
            selection.append(new_manager)
        return selection


class SPPBasketEntitlementManager(models.Model):
    _name = "g2p.program.entitlement.manager.basket"
    _inherit = [
        "g2p.base.program.entitlement.manager",
        "g2p.manager.source.mixin",
    ]
    _description = "Entitlement Basket Manager"

    # Set to False so that the UI will not display the payment management components
    IS_CASH_ENTITLEMENT = False

    @api.model
    def _default_warehouse_id(self):
        return self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.company.id)], limit=1
        )

    # Basket Entitlement Manager
    entitlement_basket_id = fields.Many2one(
        "spp.entitlement.basket", "Entitlement Basket"
    )
    entitlement_item_ids = fields.One2many(
        "g2p.program.entitlement.manager.basket.item",
        "entitlement_id",
        "Entitlement Items",
    )

    # Inventory integration fields
    warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Warehouse",
        required=True,
        default=_default_warehouse_id,
        check_company=True,
    )
    company_id = fields.Many2one(
        "res.company", string="Company", related="program_id.company_id"
    )

    # Group able to validate the payment
    entitlement_validation_group_id = fields.Many2one(
        "res.groups", string="Entitlement Validation Group"
    )

    def prepare_entitlements(self, cycle, beneficiaries):
        if not self.entitlement_item_ids:
            raise UserError(
                _("There are no items entered for this entitlement manager.")
            )

        beneficiaries_ids = beneficiaries.mapped("partner_id.id")
        for rec in self.entitlement_item_ids:
            # Get beneficiaries_with_entitlements to prevent generating
            # the same entitlement for beneficiaries
            beneficiaries_with_entitlements = (
                self.env["g2p.entitlement.inkind"]
                .search(
                    [
                        ("cycle_id", "=", cycle.id),
                        ("partner_id", "in", beneficiaries_ids),
                    ]
                )
                .mapped("partner_id.id")
            )
            entitlements_to_create = [
                beneficiaries_id
                for beneficiaries_id in beneficiaries_ids
                if beneficiaries_id not in beneficiaries_with_entitlements
            ]

            entitlement_start_validity = cycle.start_date
            entitlement_end_validity = cycle.end_date

            beneficiaries_with_entitlements_to_create = self.env["res.partner"].browse(
                entitlements_to_create
            )

            entitlements = []

            for beneficiary_id in beneficiaries_with_entitlements_to_create:
                # TODO: Determine if there's a need for multiplier
                # multiplier = 1

                entitlements.append(
                    {
                        "cycle_id": cycle.id,
                        "partner_id": beneficiary_id.id,
                        "total_amount": rec.product_id.list_price * rec.qty,
                        "product_id": rec.product_id.id,
                        "qty": rec.qty,
                        "uom_id": rec.uom_id.id,
                        "warehouse_id": self.warehouse_id
                        and self.warehouse_id.id
                        or None,
                        "state": "draft",
                        "valid_from": entitlement_start_validity,
                        "valid_until": entitlement_end_validity,
                    }
                )
            self.env["g2p.entitlement.inkind"].create(entitlements)

    def validate_entitlements(self, cycle, cycle_memberships):
        # TODO: Change the status of the entitlements to `validated` for this members.
        # move the funds from the program's wallet to the wallet of each Beneficiary that are validated
        pass

    def approve_entitlements(self, entitlements):
        state_err = 0
        message = ""
        sw = 0
        for rec in entitlements:
            if rec.state in ("draft", "pending_validation"):
                rec._action_launch_stock_rule()
                rec.update(
                    {
                        "state": "approved",
                        "date_approved": fields.Date.today(),
                    }
                )
            else:
                state_err += 1
                if sw == 0:
                    sw = 1
                    message = _(
                        "Entitlement State Error! Entitlements not in 'pending validation' state:\n"
                    )
                message += _("Program: %(prg)s, Beneficiary: %(partner)s.\n") % {
                    "prg": rec.cycle_id.program_id.name,
                    "partner": rec.partner_id.name,
                }

        return (state_err, message)

    def open_entitlements_form(self, cycle):
        self.ensure_one()
        action = {
            "name": _("Cycle Basket Entitlements"),
            "type": "ir.actions.act_window",
            "res_model": "g2p.entitlement.inkind",
            "context": {
                "create": False,
                "default_cycle_id": cycle.id,
            },
            "view_mode": "list,form",
            "views": [
                [self.env.ref("spp_programs.view_entitlement_inkind_tree").id, "tree"],
                [
                    self.env.ref("spp_programs.view_entitlement_inkind_form").id,
                    "form",
                ],
            ],
            "domain": [("cycle_id", "=", cycle.id)],
        }
        return action

    def open_entitlement_form(self, rec):
        return {
            "name": "Entitlement",
            "view_mode": "form",
            "res_model": "g2p.entitlement.inkind",
            "res_id": rec.id,
            "view_id": self.env.ref("spp_programs.view_entitlement_inkind_form").id,
            "type": "ir.actions.act_window",
            "target": "new",
        }


class G2PBasketEntitlementItem(models.Model):
    _name = "g2p.program.entitlement.manager.basket.item"
    _description = "Basket Entitlement Manager Items"
    _order = "id"

    entitlement_id = fields.Many2one(
        "g2p.program.entitlement.manager.basket", "Basket Entitlement", required=True
    )

    product_id = fields.Many2one(
        "product.product", "Product", domain=[("type", "=", "product")], required=True
    )

    qty = fields.Integer("QTY", default=1, required=True)
    uom_id = fields.Many2one(
        "uom.uom", "Unit of Measure", related="product_id.uom_id", store=True
    )
