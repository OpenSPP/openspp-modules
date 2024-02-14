# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

# from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class G2PCreateNewProgramWiz(models.TransientModel):
    _inherit = "g2p.program.create.wizard"

    @api.model
    def _default_warehouse_id(self):
        return self.env["stock.warehouse"].search([("company_id", "=", self.env.company.id)], limit=1)

    # In-Kind Entitlement Manager
    evaluate_single_item = fields.Boolean("Evaluate one item", default=False)
    entitlement_kind = fields.Selection(selection_add=[("inkind", "In-Kind")])

    entitlement_item_ids = fields.One2many(
        "g2p.program.create.wizard.entitlement.item", "program_id", "Entitlement Items"
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

    def _check_required_fields(self):
        res = super()._check_required_fields()
        if self.entitlement_kind == "inkind":
            if not self.entitlement_item_ids:
                raise UserError(_("Items are required in the In-kind entitlement manager."))
            if self.manage_inventory and not self.warehouse_id:
                raise UserError(
                    _("For inventory management, the warehouse is required in the In-kind entitlement manager.")
                )
        return res

    def _get_entitlement_manager(self, program_id):
        res = super()._get_entitlement_manager(program_id)
        if self.entitlement_kind == "inkind":
            # Add a new record to in-kind entitlement manager model
            entitlement_item_ids = []
            for item in self.entitlement_item_ids:
                entitlement_item_ids.append(
                    [
                        0,
                        0,
                        {
                            "sequence": item.sequence,
                            "product_id": item.product_id.id,
                            "qty": item.qty,
                            "condition": item.condition,
                            "multiplier_field": item.multiplier_field.id,
                            "max_multiplier": item.max_multiplier,
                        },
                    ]
                )

            def_mgr_obj = "g2p.program.entitlement.manager.inkind"
            def_mgr = self.env[def_mgr_obj].create(
                {
                    "name": "In-kind",
                    "program_id": program_id,
                    "evaluate_single_item": self.evaluate_single_item,
                    "entitlement_item_ids": entitlement_item_ids,
                    "entitlement_validation_group_id": self.entitlement_validation_group_id.id,
                    "id_type": self.id_type.id,
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
    _name = "g2p.program.create.wizard.entitlement.item"
    _description = "Create a New Program Wizard Entitlement Items"
    _order = "sequence,id"

    sequence = fields.Integer(default=1000)
    program_id = fields.Many2one("g2p.program.create.wizard", "New Program", required=True)

    product_id = fields.Many2one("product.product", "Product", domain=[("type", "=", "product")], required=True)

    condition = fields.Char("Condition Domain")
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

    qty = fields.Integer("QTY", default=1, required=True)
    uom_id = fields.Many2one("uom.uom", "Unit of Measure", related="product_id.uom_id")
