# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, fields, models
from odoo.exceptions import UserError

# from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class G2PCreateNewProgramWiz(models.TransientModel):
    _inherit = "g2p.program.create.wizard"

    # Cash Entitlement Manager
    evaluate_one_item = fields.Boolean(default=False)
    entitlement_kind = fields.Selection(selection_add=[("cash", "Cash")])

    entitlement_cash_item_ids = fields.One2many(
        "g2p.program.create.wizard.entitlement.cash.item",
        "program_id",
        "Cash Entitlement Items",
    )

    max_amount = fields.Monetary(
        string="Maximum Amount",
        currency_field="currency_id",
        default=0.0,
    )

    def _check_required_fields(self):
        res = super()._check_required_fields()
        if self.entitlement_kind == "cash" and not self.entitlement_cash_item_ids:
            raise UserError(_("Items are required in the Cash entitlement manager."))
        return res

    def _get_entitlement_manager(self, program_id):
        res = super()._get_entitlement_manager(program_id)
        if self.entitlement_kind == "cash":
            # Add a new record to cash entitlement manager model
            entitlement_item_ids = []
            for item in self.entitlement_cash_item_ids:
                entitlement_item_ids.append(
                    [
                        0,
                        0,
                        {
                            "sequence": item.sequence,
                            "amount": item.amount,
                            "currency_id": item.currency_id.id,
                            "condition": item.condition,
                            "multiplier_field": item.multiplier_field.id,
                            "max_multiplier": item.max_multiplier,
                        },
                    ]
                )

            def_mgr_obj = "g2p.program.entitlement.manager.cash"
            def_mgr = self.env[def_mgr_obj].create(
                {
                    "name": "Cash",
                    "program_id": program_id,
                    "evaluate_one_item": self.evaluate_one_item,
                    "entitlement_item_ids": entitlement_item_ids,
                    "max_amount": self.max_amount,
                    "entitlement_validation_group_id": self.entitlement_validation_group_id.id,
                    "id_type": self.id_type.id,
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


class G2PCreateNewProgramWizCashItem(models.TransientModel):
    _name = "g2p.program.create.wizard.entitlement.cash.item"
    _description = "Create a New Program Wizard Entitlement Cash Items"
    _order = "sequence,id"

    sequence = fields.Integer(default=1000)
    program_id = fields.Many2one("g2p.program.create.wizard", "New Program", required=True)

    amount = fields.Monetary(
        currency_field="currency_id",
        group_operator="sum",
        default=0.0,
        string="Amount per cycle",
        required=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="program_id.currency_id",
        readonly=True,
    )

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
