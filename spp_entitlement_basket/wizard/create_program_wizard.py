# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError

# from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class G2PCreateNewProgramWiz(models.TransientModel):
    _inherit = "g2p.program.create.wizard"

    @api.model
    def _default_warehouse_id(self):
        return self.env["stock.warehouse"].search([("company_id", "=", self.env.company.id)], limit=1)

    # Basket Entitlement Manager
    entitlement_kind = fields.Selection(selection_add=[("basket_entitlement", "Basket Entitlement")])
    entitlement_basket_id = fields.Many2one("spp.entitlement.basket", "Entitlement Basket")
    basket_product_ids = fields.One2many(related="entitlement_basket_id.product_ids")
    basket_entitlement_item_ids = fields.One2many(
        "g2p.program.create.wizard.basket.entitlement.item",
        "program_id",
        "Entitlement Items",
    )

    multiplier_field = fields.Many2one(
        "ir.model.fields",
        "Multiplier",
        domain=[("model_id.model", "=", "res.partner"), ("ttype", "=", "integer")],
    )
    max_multiplier = fields.Integer(
        default=0,
        string="Maximum number",
        help="0 means no limit",
    )

    # Inventory integration fields
    manage_inventory = fields.Boolean(default=False)
    warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Warehouse",
        default=_default_warehouse_id,
        check_company=True,
    )
    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env.company)

    @api.onchange("entitlement_kind")
    def _onchange_entitlement_kind(self):
        if self.entitlement_kind == "basket_entitlement":
            self.target_type = "group"

    @api.onchange("entitlement_basket_id")
    def _onchange_entitlement_basket_id(self):
        if self.basket_entitlement_item_ids:
            # Clear self.basket_entitlement_item_ids first
            self.update({"basket_entitlement_item_ids": [(Command.clear())]})
        basket_entitlement_item_ids = []
        for rec in self.entitlement_basket_id.product_ids:
            vals = {
                "product_id": rec.product_id.id,
                "qty": rec.qty,
                "uom_id": rec.uom_id.id,
            }
            basket_entitlement_item_ids.append(Command.create(vals))
        # _logger.info("DEBUG: %s" % basket_entitlement_item_ids)
        self.update({"basket_entitlement_item_ids": basket_entitlement_item_ids})

    def _check_required_fields(self):
        res = super()._check_required_fields()
        if self.entitlement_kind == "basket_entitlement":
            if not self.entitlement_basket_id:
                raise UserError(_("The Food Basket in Cycle Manager is required in the Basket entitlement manager."))
            if not self.basket_product_ids:
                raise UserError(_("Items are required in the Basket entitlement manager."))
            if self.manage_inventory and not self.warehouse_id:
                raise UserError(
                    _("For inventory management, the warehouse is required in the basket entitlement manager.")
                )
        return res

    def _get_entitlement_manager(self, program_id):
        res = super()._get_entitlement_manager(program_id)
        if self.entitlement_kind == "basket_entitlement":
            # Add a new record to basket entitlement manager model
            entitlement_item_ids = []
            for item in self.basket_product_ids:
                entitlement_item_ids.append(
                    [
                        0,
                        0,
                        {
                            "product_id": item.product_id.id,
                            "qty": item.qty,
                        },
                    ]
                )

            def_mgr_obj = "g2p.program.entitlement.manager.basket"
            def_mgr = self.env[def_mgr_obj].create(
                {
                    "name": "Food Basket",
                    "program_id": program_id,
                    "entitlement_basket_id": self.entitlement_basket_id.id,
                    "entitlement_item_ids": entitlement_item_ids,
                    "multiplier_field": self.multiplier_field.id,
                    "max_multiplier": self.max_multiplier,
                    "entitlement_validation_group_id": self.entitlement_validation_group_id.id,
                    "manage_inventory": self.manage_inventory,
                    "warehouse_id": self.warehouse_id.id,
                }
            )

            # Add a new record to entitlement manager parent model
            man_obj = self.env["g2p.program.entitlement.manager"]
            mgr = man_obj.create(
                {
                    "program_id": program_id,
                    "manager_ref_id": f"{def_mgr_obj},{str(def_mgr.id)}",
                }
            )
            res = {"entitlement_managers": [(4, mgr.id)]}
        return res


class G2PCreateNewProgramWizItem(models.TransientModel):
    _name = "g2p.program.create.wizard.basket.entitlement.item"
    _description = "Create a New Program Wizard basket Entitlement Items"
    _order = "id"

    program_id = fields.Many2one("g2p.program.create.wizard", "New Program", required=True)

    product_id = fields.Many2one("product.product", "Product", domain=[("type", "=", "product")], required=True)
    qty = fields.Integer("QTY", default=1, required=True)
    uom_id = fields.Many2one("uom.uom", "Unit of Measure", related="product_id.uom_id")
