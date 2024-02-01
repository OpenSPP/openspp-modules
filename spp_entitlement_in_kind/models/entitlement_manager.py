# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.queue_job.delay import group

_logger = logging.getLogger(__name__)


class EntitlementManager(models.Model):
    _inherit = "g2p.program.entitlement.manager"

    @api.model
    def _selection_manager_ref_id(self):
        selection = super()._selection_manager_ref_id()
        new_manager = ("g2p.program.entitlement.manager.inkind", "In-Kind")
        if new_manager not in selection:
            selection.append(new_manager)
        return selection


class G2PInKindEntitlementManager(models.Model):
    _name = "g2p.program.entitlement.manager.inkind"
    _inherit = [
        "g2p.base.program.entitlement.manager",
        "g2p.manager.source.mixin",
    ]
    _description = "In-Kind Entitlement Manager"

    # Set to False so that the UI will not display the payment management components
    IS_CASH_ENTITLEMENT = False

    @api.model
    def _default_warehouse_id(self):
        return self.env["stock.warehouse"].search([("company_id", "=", self.env.company.id)], limit=1)

    # In-Kind Entitlement Manager
    evaluate_single_item = fields.Boolean("Evaluate one item", default=False)
    entitlement_item_ids = fields.One2many(
        "g2p.program.entitlement.manager.inkind.item",
        "entitlement_id",
        "Entitlement Items",
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
        """Prepare In-Kind Entitlements.
        This method is used to prepare the in-kind entitlement list of the beneficiaries.
        :param cycle: The cycle.
        :param beneficiaries: The beneficiaries.
        :return:
        """
        if not self.entitlement_item_ids:
            raise UserError(_("There are no items entered for this entitlement manager."))

        all_beneficiaries_ids = beneficiaries.mapped("partner_id.id")
        for rec in self.entitlement_item_ids:
            if rec.condition:
                # Filter res.partner based on entitlement condition and get ids
                domain = [("id", "in", all_beneficiaries_ids)]
                domain += self._safe_eval(rec.condition)
                beneficiaries_ids = self.env["res.partner"].search(domain).ids

                # Check if single evaluation
                if self.evaluate_single_item:
                    # Remove beneficiaries_ids from all_beneficiaries_ids
                    for bid in beneficiaries_ids:
                        if bid in all_beneficiaries_ids:
                            all_beneficiaries_ids.remove(bid)
            else:
                beneficiaries_ids = all_beneficiaries_ids

            # Get beneficiaries_with_entitlements to prevent generating
            # the same entitlement for beneficiaries
            beneficiaries_with_entitlements = (
                self.env["g2p.entitlement.inkind"]
                .search(
                    [
                        ("cycle_id", "=", cycle.id),
                        ("partner_id", "in", beneficiaries_ids),
                        ("inkind_item_id", "=", rec.id),
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
                multiplier = 1
                if rec.multiplier_field:
                    # Get the multiplier value from multiplier_field else return the default multiplier=1
                    multiplier = beneficiary_id.mapped(rec.multiplier_field.name)
                    if multiplier:
                        multiplier = multiplier[0] or 1
                if rec.max_multiplier > 0 and multiplier > rec.max_multiplier:
                    multiplier = rec.max_multiplier
                qty = multiplier * rec.qty

                entitlement_fields = {
                    "cycle_id": cycle.id,
                    "partner_id": beneficiary_id.id,
                    "total_amount": rec.product_id.list_price * qty,
                    "product_id": rec.product_id.id,
                    "qty": qty,
                    "unit_price": rec.product_id.list_price,
                    "uom_id": rec.uom_id.id,
                    "manage_inventory": self.manage_inventory,
                    "warehouse_id": self.warehouse_id and self.warehouse_id.id or None,
                    "inkind_item_id": rec.id,
                    "state": "draft",
                    "valid_from": entitlement_start_validity,
                    "valid_until": entitlement_end_validity,
                }
                # Check if there are additional fields to be added in entitlements
                addl_fields = self._get_addl_entitlement_fields(beneficiary_id)
                if addl_fields:
                    entitlement_fields.update(addl_fields)
                entitlements.append(entitlement_fields)

            if entitlements:
                self.env["g2p.entitlement.inkind"].create(entitlements)

    def _get_addl_entitlement_fields(self, beneficiary_id):
        """
        This function must be overriden to add additional field to be written in the entitlements.
        Add the id_number from the beneficiaries based on the id_type configured in entitlement manager.
        """
        retval = None
        if self.id_type:
            id_docs = beneficiary_id.reg_ids.filtered(lambda a: a.id_type.id == self.id_type.id)
            if id_docs:
                id_number = id_docs[0].value
                retval = {
                    "id_number": id_number,
                }
        return retval

    def set_pending_validation_entitlements(self, cycle):
        """Set In-Kind Entitlements to Pending Validation.
        In-kind Entitlement Manager :meth:`set_pending_validation_entitlements`.
        Set entitlements to pending_validation in a cycle.

        :param cycle: A recordset of cycle
        :return:
        """
        # Get the number of entitlements in cycle
        entitlements_count = cycle.get_entitlements(
            ["draft"],
            entitlement_model="g2p.entitlement.inkind",
            count=True,
        )
        if entitlements_count < self.MIN_ROW_JOB_QUEUE:
            self._set_pending_validation_entitlements(cycle)

        else:
            self._set_pending_validation_entitlements_async(cycle, entitlements_count)

    def _set_pending_validation_entitlements_async(self, cycle, entitlements_count):
        """Set Entitlements to Pending Validation
        In-kind Entitlement Manager :meth:`_set_pending_validation_entitlements_async`
        Asynchronous setting of entitlements to pending_validation in a cycle using `job_queue`

        :param cycle: A recordset of cycle
        :param entitlements_count: Integer - total number of entitlements to process
        :return:
        """
        _logger.debug("Set entitlements to pending validation asynchronously")
        cycle.message_post(
            body=_(
                "Setting %s entitlements to pending validation has started.",
                entitlements_count,
            )
        )
        cycle.write(
            {
                "locked": True,
                "locked_reason": _("Set entitlements to pending validation for cycle."),
            }
        )

        jobs = []
        for i in range(0, entitlements_count, self.MAX_ROW_JOB_QUEUE):
            jobs.append(
                self.delayable()._set_pending_validation_entitlements(cycle, offset=i, limit=self.MAX_ROW_JOB_QUEUE)
            )
        main_job = group(*jobs)
        main_job.on_done(self.delayable().mark_job_as_done(cycle, _("Entitlements Set to Pending Validation.")))
        main_job.delay()

    def _set_pending_validation_entitlements(self, cycle, offset=0, limit=None):
        """Set In-Kind Entitlements to Pending Validation.
        In-kind Entitlement Manager :meth:`_set_pending_validation_entitlements`.
        Set entitlements to pending_validation in a cycle.

        :param cycle: A recordset of cycle
        :param offset: An integer value to be used in :meth:`cycle.get_entitlements` for setting the query offset
        :param limit: An integer value to be used in :meth:`cycle.get_entitlements` for setting the query limit
        :return:
        """
        # Get the entitlements in the cycle
        entitlements = cycle.get_entitlements(
            ["draft"],
            entitlement_model="g2p.entitlement.inkind",
            offset=offset,
            limit=limit,
        )
        entitlements.update({"state": "pending_validation"})

    def validate_entitlements(self, cycle):
        """Validate In-Kind Entitlements.
        In-Kind Entitlement Manager :meth:`validate_entitlements`.
        Validate entitlements in a cycle

        :param cycle: A recordset of cycle
        :return:
        """
        # Get the number of entitlements in cycle
        entitlements_count = cycle.get_entitlements(
            ["draft", "pending_validation"],
            entitlement_model="g2p.entitlement.inkind",
            count=True,
        )
        if entitlements_count < self.MIN_ROW_JOB_QUEUE:
            err, message = self._validate_entitlements(cycle)
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
            self._validate_entitlements_async(cycle, entitlements_count)

    def _validate_entitlements_async(self, cycle, entitlements_count):
        """Validate Entitlements
        In-kind Entitlement Manager :meth:`_validate_entitlements_async`
        Asynchronous validation of entitlements in a cycle using `job_queue`

        :param cycle: A recordset of cycle
        :param entitlements: A recordset of entitlements to validate
        :param entitlements_count: Integer count of entitlements to validate
        :return:
        """
        _logger.debug("Validate entitlements asynchronously")
        cycle.message_post(body=_("Validate %s entitlements started.", entitlements_count))
        cycle.write(
            {
                "locked": True,
                "locked_reason": _("Validate and approve entitlements for cycle."),
            }
        )

        jobs = []
        for i in range(0, entitlements_count, self.MAX_ROW_JOB_QUEUE):
            jobs.append(self.delayable()._validate_entitlements(cycle, offset=i, limit=self.MAX_ROW_JOB_QUEUE))
        main_job = group(*jobs)
        main_job.on_done(self.delayable().mark_job_as_done(cycle, _("Entitlements Validated and Approved.")))
        main_job.delay()

    def _validate_entitlements(self, cycle, offset=0, limit=None):
        """Validate In-Kind Entitlements.
        In-Kind Entitlement Manager :meth:`_validate_entitlements`.
        Validate entitlements in a cycle.

        :param cycle: A recordset of cycle
        :param offset: An integer value to be used in :meth:`cycle.get_entitlements` for setting the query offset
        :param limit: An integer value to be used in :meth:`cycle.get_entitlements` for setting the query limit
        :return err: Integer number of errors
        :return message: String description of the error
        """
        # Get the entitlements in the cycle
        entitlements = cycle.get_entitlements(
            ["draft", "pending_validation"],
            entitlement_model="g2p.entitlement.inkind",
            offset=offset,
            limit=limit,
        )
        err, message = self.approve_entitlements(entitlements)
        return err, message

    def cancel_entitlements(self, cycle):
        """Cancel In-Kind Entitlements.
        In-Kind Entitlement Manager :meth:`cancel_entitlements`
        Cancel entitlements in a cycle.

        :param cycle: A recordset of cycle
        :return:
        """
        # Get the total number of entitlements
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
        """Cancel In-Kind Entitlements.
        In-Kind Entitlement Manager :meth:`_cancel_entitlements`.
        Cancel entitlements in a cycle.

        :param entitlements: A recordset of entitlements to cancel
        :return:
        """
        entitlements.update({"state": "cancelled"})

    def approve_entitlements(self, entitlements):
        """Approve In-Kind Entitlements.
        In-Kind Entitlement Manager :meth:`_approve_entitlements`.
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
        self.ensure_one()
        action = {
            "name": _("In-Kind Entitlements"),
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


class G2PInKindEntitlementItem(models.Model):
    _name = "g2p.program.entitlement.manager.inkind.item"
    _description = "In-Kind Entitlement Manager Items"
    _order = "sequence,id"

    sequence = fields.Integer(default=1000)
    entitlement_id = fields.Many2one("g2p.program.entitlement.manager.inkind", "In-kind Entitlement", required=True)

    product_id = fields.Many2one("product.product", "Product", domain=[("type", "=", "product")], required=True)

    # non-mandatory field to store a domain that is used to verify if this item is valid for a beneficiary
    # For example, it could be: [('is_woman_headed_household, '=', True)]
    # If the condition is not met, this calculation is not used
    condition = fields.Char("Condition Domain")

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

    qty = fields.Integer("QTY", default=1, required=True)
    uom_id = fields.Many2one("uom.uom", "Unit of Measure", related="product_id.uom_id", store=True)
