import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

# from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class G2PCreateNewProgramWiz(models.TransientModel):
    _inherit = "g2p.program.create.wizard"

    @api.model
    def _default_warehouse_id(self):
        return self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.company.id)], limit=1
        )

    # Basket Entitlement Manager
    entitlement_kind = fields.Selection(selection_add=[("basket_entitlement", "Basket Entitlement")])

    basket_entitlement_item_ids = fields.One2many(
        "g2p.program.create.wizard.basket.entitlement.item",
        "program_id",
        "Entitlement Items",
    )

    # Inventory integration fields
    warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Warehouse",
        default=_default_warehouse_id,
        check_company=True,
    )
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )

    def _check_required_fields(self):
        res = super()._check_required_fields()
        if self.entitlement_kind == "basket_entitlement":
            if not self.basket_entitlement_item_ids:
                raise UserError(_("Items are required in the Basket entitlement manager."))
            if not self.warehouse_id:
                raise UserError(
                    _(
                        "For inventory management, the warehouse is required in the basket entitlement manager."
                    )
                )
        return res

    def _get_entitlement_manager(self, program_id):
        res = super()._get_entitlement_manager(program_id)
        if self.entitlement_kind == "basket_entitlement":
            # Add a new record to basket entitlement manager model
            entitlement_item_ids = []
            for item in self.basket_entitlement_item_ids:
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
                    "name": "basket",
                    "program_id": program_id,
                    "basket_entitlement_item_ids": entitlement_item_ids,
                    "entitlement_validation_group_id": self.entitlement_validation_group_id.id,
                    "warehouse_id": self.warehouse_id.id,
                }
            )

            # Add a new record to entitlement manager parent model
            man_obj = self.env["g2p.program.entitlement.manager"]
            mgr = man_obj.create(
                {
                    "program_id": program_id,
                    "manager_ref_id": "%s,%s" % (def_mgr_obj, str(def_mgr.id)),
                }
            )
            res = {"entitlement_managers": [(4, mgr.id)]}
        return res


class G2PCreateNewProgramWizItem(models.TransientModel):
    _name = "g2p.program.create.wizard.basket.entitlement.item"
    _description = "Create a New Program Wizard basket Entitlement Items"
    _order = "id"

    program_id = fields.Many2one(
        "g2p.program.create.wizard", "New Program", required=True
    )

    product_id = fields.Many2one(
        "product.product", "Product", domain=[("type", "=", "product")], required=True
    )
    qty = fields.Integer("QTY", default=1, required=True)
    uom_id = fields.Many2one("uom.uom", "Unit of Measure", related="product_id.uom_id")
