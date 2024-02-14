# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


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
    """
    SPPBasketEntitlementManager is the model for the food basket entitlement manager.
    It provides all the functions for processing food basket entitlements.

    """

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
        return self.env["stock.warehouse"].search([("company_id", "=", self.env.company.id)], limit=1)

    # Basket Entitlement Manager
    entitlement_basket_id = fields.Many2one(
        "spp.entitlement.basket", "Entitlement Basket"
    )  #: Food basket configured for entitlement
    entitlement_item_ids = fields.One2many(
        "g2p.program.entitlement.manager.basket.item",
        "entitlement_id",
        "Entitlement Items",
    )  #: Details of the food basket (products, QTY, UoM)

    basket_product_ids = fields.One2many(related="entitlement_basket_id.product_ids")

    # any field that is an integer of `res.partner`
    # It could be the number of members, children, elderly, or any other metrics.
    # if no multiplier field is set, it is considered as 1.
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
        required=True,
        default=_default_warehouse_id,
        check_company=True,
    )
    company_id = fields.Many2one("res.company", string="Company", related="program_id.company_id")

    # Group able to validate the payment
    entitlement_validation_group_id = fields.Many2one("res.groups", string="Entitlement Validation Group")

    def prepare_entitlements(self, cycle, beneficiaries):
        """Prepare Basket Entitlements.
        Basket Entitlement Manager :meth:`prepare_entitlements`.
        This method is used to prepare the entitlement list of the beneficiaries.
        :param cycle: The cycle.
        :param beneficiaries: The beneficiaries.
        :return:
        """
        if not self.entitlement_item_ids:
            raise UserError(_("There are no items entered for this entitlement manager."))

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
                        ("product_id", "=", rec.product_id.id),
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

            beneficiaries_with_entitlements_to_create = self.env["res.partner"].browse(entitlements_to_create)

            entitlements = []

            for beneficiary_id in beneficiaries_with_entitlements_to_create:
                # Check service point product_ids
                if beneficiary_id.service_point_ids and beneficiary_id.service_point_ids.product_ids:
                    service_point_product_ids = beneficiary_id.service_point_ids.mapped("product_ids.id")
                    if rec.product_id.id in service_point_product_ids:
                        service_point_id = beneficiary_id.service_point_ids
                        # raise UserError("DEBUG: %s" % service_point_id[0])
                        # TODO: Check inventory
                        entitlements.append(
                            {
                                "cycle_id": cycle.id,
                                "partner_id": beneficiary_id.id,
                                "service_point_id": service_point_id[0].id,
                                "total_amount": rec.product_id.list_price * rec.qty,
                                "product_id": rec.product_id.id,
                                "qty": rec.qty,
                                "unit_price": rec.product_id.list_price,
                                "uom_id": rec.uom_id.id,
                                "manage_inventory": self.manage_inventory,
                                "warehouse_id": self.warehouse_id and self.warehouse_id.id or None,
                                "state": "draft",
                                "valid_from": entitlement_start_validity,
                                "valid_until": entitlement_end_validity,
                            }
                        )
            if entitlements:
                self.env["g2p.entitlement.inkind"].create(entitlements)

    def set_pending_validation_entitlements(self, cycle):
        """Set Basket Entitlements to Pending Validation.
        Basket Entitlement Manager :meth:`set_pending_validation_entitlements`.
        Set entitlements to pending_validation in a cycle.

        :param cycle: A recordset of cycle
        :return:
        """
        # Get the number of entitlements
        entitlements_count = cycle.get_entitlements(["draft"], entitlement_model="g2p.entitlement.inkind", count=True)

        # Get the entitlements
        entitlements = cycle.get_entitlements(
            ["draft"],
            entitlement_model="g2p.entitlement.inkind",
        )

        if entitlements_count < self.MIN_ROW_JOB_QUEUE:
            self._set_pending_validation_entitlements(entitlements)

        else:
            self._set_pending_validation_entitlements_async(cycle, entitlements)

    def _set_pending_validation_entitlements(self, entitlements):
        """Set Basket Entitlements to Pending Validation.
        Basket Entitlement Manager :meth:`_set_pending_validation_entitlements`.
        Set entitlements to pending_validation in a cycle.

        :param entitlements: A recordset of entitlements to process
        :return:
        """
        entitlements.update({"state": "pending_validation"})
        # _logger.debug("Entitlement Validation: total: %s" % (len(entitlements)))

    def validate_entitlements(self, cycle):
        """Validate Basket Entitlements.
        Basket Entitlement Manager :meth:`validate_entitlements`.
        Validate entitlements in a cycle.

        :param cycle: A recordset of cycle
        :return:
        """
        # Get the number of entitlements
        entitlements_count = cycle.get_entitlements(
            ["draft", "pending_validation"],
            entitlement_model="g2p.entitlement.inkind",
            count=True,
        )

        # Get the entitlements
        entitlements = cycle.get_entitlements(
            ["draft", "pending_validation"],
            entitlement_model="g2p.entitlement.inkind",
        )

        if entitlements_count < self.MIN_ROW_JOB_QUEUE:
            err, message = self._validate_entitlements(entitlements)
            if err > 0:
                kind = "danger"
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Entitlement"),
                        "message": message,
                        "sticky": True,
                        "type": kind,
                        "next": {
                            "type": "ir.actions.act_window_close",
                        },
                    },
                }
            else:
                kind = "success"
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Entitlement"),
                        "message": _("Entitlements are validated and approved."),
                        "sticky": True,
                        "type": kind,
                        "next": {
                            "type": "ir.actions.act_window_close",
                        },
                    },
                }
        else:
            self._validate_entitlements_async(cycle, entitlements, entitlements_count)

    def _validate_entitlements(self, entitlements):
        """Validate Basket Entitlements.
        Basket Entitlement Manager :meth:`_validate_entitlements`.
        Validate entitlements in a cycle

        :param entitlements: A recordset of entitlements to validate
        :return err: Integer number of errors
        :return message: String description of the error
        """
        err, message = self.approve_entitlements(entitlements)
        return err, message

    def cancel_entitlements(self, cycle):
        """Cancel Basket Entitlements.
        Basket Entitlement Manager :meth:`cancel_entitlements`.
        Cancel entitlements in a cycle.

        :param cycle: A recordset of cycle
        :return:
        """
        # Get the number of entitlements
        entitlements_count = cycle.get_entitlements(
            ["draft", "pending_validation", "approved"],
            entitlement_model="g2p.entitlement.inkind",
            count=True,
        )

        # Get the entitlements
        entitlements = cycle.get_entitlements(
            ["draft", "pending_validation", "approved"],
            entitlement_model="g2p.entitlement.inkind",
        )

        if entitlements_count < self.MIN_ROW_JOB_QUEUE:
            self._cancel_entitlements(entitlements)
        else:
            self._cancel_entitlements_async(cycle, entitlements, entitlements_count)

    def _cancel_entitlements(self, entitlements):
        """Cancel Basket Entitlements.
        Basket Entitlement Manager :meth:`_cancel_entitlements`.
        Synchronous cancellation of entitlements in a cycle.

        :param entitlements: A recordset of entitlements to cancel
        :return:
        """
        entitlements.update({"state": "cancelled"})

    def approve_entitlements(self, entitlements):
        """Approve Basket Entitlements.
        Basket Entitlement Manager :meth:`_approve_entitlements`.
        Approve selected entitlements.

        :param entitlements: Selected entitlements to approve
        :return state_err: Integer number of errors
        :return message: String description of the errors
        """
        state_err = 0
        message = ""
        sw = 0
        for rec in entitlements:
            if rec.state in ("draft", "pending_validation"):
                if rec.manage_inventory:
                    # TODO: check if there is enough stocks to allocate
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
                    message = _("Entitlement State Error! Entitlements not in 'pending validation' state:\n")
                message += _("Program: %(prg)s, Beneficiary: %(partner)s.\n") % {
                    "prg": rec.cycle_id.program_id.name,
                    "partner": rec.partner_id.name,
                }

        return (state_err, message)

    def open_entitlements_form(self, cycle):
        """Open Entitlements Form.

        :param cycle: recordset of the cycle
        :return:
        """
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

    entitlement_id = fields.Many2one("g2p.program.entitlement.manager.basket", "Basket Entitlement", required=True)

    product_id = fields.Many2one("product.product", "Product", domain=[("type", "=", "product")], required=True)

    qty = fields.Integer("QTY", default=1, required=True)
    uom_id = fields.Many2one("uom.uom", "Unit of Measure", related="product_id.uom_id", store=True)
