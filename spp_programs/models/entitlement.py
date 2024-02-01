# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging
from uuid import uuid4

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare

from . import constants

_logger = logging.getLogger(__name__)


class InKindEntitlement(models.Model):
    _name = "g2p.entitlement.inkind"
    _description = "Entitlement"
    _order = "id desc"
    _check_company_auto = True

    @api.model
    def _generate_code(self):
        return str(uuid4())[4:-8][3:]

    name = fields.Char(compute="_compute_name")
    code = fields.Char(default=lambda x: x._generate_code(), required=True, readonly=True, copy=False)

    partner_id = fields.Many2one(
        "res.partner",
        "Registrant",
        help="A beneficiary",
        required=True,
        ondelete="cascade",
        domain=[("is_registrant", "=", True)],
        index=True,
    )
    id_number = fields.Char()

    service_point_id = fields.Many2one("spp.service.point", "Service Point")

    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)

    cycle_id = fields.Many2one("g2p.cycle", required=True)
    program_id = fields.Many2one("g2p.program", related="cycle_id.program_id")

    # Product Fields
    product_id = fields.Many2one("product.product", "Product", domain=[("type", "=", "product")])
    qty = fields.Integer("QTY", default=1)
    unit_price = fields.Monetary(string="Value/Unit", currency_field="currency_id")
    uom_id = fields.Many2one("uom.uom", "Unit of Measure")

    # Inventory integration fields
    manage_inventory = fields.Boolean(default=False)
    warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Warehouse",
    )
    route_id = fields.Many2one("stock.route", string="Route", ondelete="restrict", check_company=True)
    move_ids = fields.One2many("stock.move", "entitlement_id", string="Stock Moves")

    # Accounting Fields
    currency_id = fields.Many2one("res.currency", readonly=True, related="journal_id.currency_id")
    total_amount = fields.Monetary(string="Total Value", currency_field="currency_id")
    journal_id = fields.Many2one(
        "account.journal",
        "Journal",
        store=True,
        compute="_compute_journal_id",
    )

    valid_from = fields.Date(required=False)
    valid_until = fields.Date(default=lambda self: fields.Date.add(fields.Date.today(), years=1))

    date_approved = fields.Date()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending_validation", "Pending Validation"),
            ("approved", "Approved"),
            ("trans2FSP", "Transferred to FSP"),
            ("rdpd2ben", "Redeemed/Paid to Beneficiary"),
            ("rejected1", "Rejected: Beneficiary didn't want the entitlement"),
            ("rejected2", "Rejected: Beneficiary account does not exist"),
            ("rejected3", "Rejected: Other reason"),
            ("cancelled", "Cancelled"),
            ("expired", "Expired"),
        ],
        "Status",
        default="draft",
        copy=False,
    )

    _sql_constraints = [
        (
            "unique_entitlement_code",
            "UNIQUE(code)",
            "The entitlement code must be unique.",
        ),
    ]

    def _get_view(self, view_id=None, view_type="list", **options):
        arch, view = super()._get_view(view_id=view_id, view_type=view_type, **options)

        group_g2p_admin = self.env.user.has_group("g2p_registry_base.group_g2p_admin")
        if not group_g2p_admin:
            if view_type != "search":
                group_g2p_registrar = self.env.user.has_group("g2p_registry_base.group_g2p_registrar")
                g2p_program_validator = self.env.user.has_group("g2p_programs.g2p_program_validator")
                g2p_program_cycle_approver = self.env.user.has_group("g2p_programs.g2p_program_cycle_approver")

                # Users with groups Registrar or Program Validator without Program Cycle Approver are not allowed
                # But users with both Program Validator and Program Cycle Approver are allowed
                if group_g2p_registrar or (g2p_program_validator and not g2p_program_cycle_approver):
                    raise ValidationError(_("You have no access in the Entitlement List View"))

        return arch, view

    @api.depends("cycle_id.program_id.journal_id")
    def _compute_journal_id(self):
        for record in self:
            record.journal_id = (
                record.cycle_id
                and record.cycle_id.program_id
                and record.cycle_id.program_id.journal_id
                and record.cycle_id.program_id.journal_id.id
                or None
            )

    def _compute_name(self):
        for record in self:
            name = _("Entitlement: (%s)", record.product_id.name)
            record.name = name

    @api.autovacuum
    def _gc_mark_expired_entitlement(self):
        self.env["g2p.entitlement"].search(
            ["&", ("state", "=", "approved"), ("valid_until", "<", fields.Date.today())]
        ).write({"state": "expired"})

    def unlink(self):
        for rec in self:
            if rec.state == "draft":
                return super().unlink()
            else:
                raise ValidationError(_("Only draft entitlements are allowed to be deleted"))

    def approve_entitlement(self):
        state_err, message = self.program_id.get_manager(constants.MANAGER_ENTITLEMENT).approve_entitlements(self)

        if state_err > 0:
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

    def open_entitlement_form(self):
        return self.program_id.get_manager(constants.MANAGER_ENTITLEMENT).open_entitlement_form(self)

    # Inventory functions
    def _prepare_procurement_values(self, group_id=False):
        """Prepare specific key for moves or other components that will be created from a stock rule
        comming from an entitlement.
        """
        self.ensure_one()
        # Use the delivery date if there is else use date_order and lead time
        # TODO: @edwin Shouldn't this be the start date cause the delivery need to be done by the time the cycle start?
        date_deadline = self.cycle_id.end_date
        date_planned = self.cycle_id.start_date
        values = {
            "group_id": group_id,
            "entitlement_id": self.id,
            "date_planned": date_planned,
            "date_deadline": date_deadline,
            "route_ids": self.route_id,
            "warehouse_id": self.warehouse_id or False,
            "partner_id": self.partner_id.id,
            "product_description_variants": self.product_id.name,
            "company_id": self.company_id,
            # 'product_packaging_id': self.product_packaging_id,
        }
        return values

    def _get_qty_procurement(self):
        self.ensure_one()
        qty = 0.0
        outgoing_moves, incoming_moves = self._get_outgoing_incoming_moves()
        for move in outgoing_moves:
            qty += move.product_uom._compute_quantity(move.product_uom_qty, self.uom_id, rounding_method="HALF-UP")
        for move in incoming_moves:
            qty -= move.product_uom._compute_quantity(move.product_uom_qty, self.uom_id, rounding_method="HALF-UP")
        return qty

    def _get_outgoing_incoming_moves(self):
        outgoing_moves = self.env["stock.move"]
        incoming_moves = self.env["stock.move"]

        moves = self.move_ids.filtered(
            lambda r: r.state != "cancel" and not r.scrapped and self.product_id == r.product_id
        )

        for move in moves:
            if move.location_dest_id.usage == "customer":
                if not move.origin_returned_move_id or (move.origin_returned_move_id and move.to_refund):
                    outgoing_moves |= move
            elif move.location_dest_id.usage != "customer" and move.to_refund:
                incoming_moves |= move

        return outgoing_moves, incoming_moves

    def _get_procurement_group(self):
        return self.cycle_id.procurement_group_id

    def _prepare_procurement_group_vals(self):
        return {
            "name": self.cycle_id.name,
            "move_type": "direct",
            "cycle_id": self.cycle_id.id,
            "partner_id": self.partner_id.id,
        }

    def _action_launch_stock_rule(self):
        """
        Launch procurement group run method with required/custom fields generated by an
        entitlement. procurement group will launch '_run_pull', '_run_buy' or '_run_manufacture'
        depending on the entitlement product rule.
        """
        if self._context.get("skip_procurement"):
            return True
        precision = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        procurements = []
        for row in self:
            row = row.with_company(row.company_id)
            if row.product_id.type not in ("consu", "product"):
                continue
            qty = row._get_qty_procurement()
            if float_compare(qty, float(row.qty), precision_digits=precision) == 0:
                continue

            group_id = row._get_procurement_group()
            if not group_id:
                group_id = self.env["procurement.group"].create(row._prepare_procurement_group_vals())
                row.cycle_id.procurement_group_id = group_id
            else:
                # In case the procurement group is already created and the entitlement was
                # cancelled, we need to update certain values of the group.
                updated_vals = {}
                if group_id.partner_id != row.partner_id:
                    updated_vals.update({"partner_id": row.partner_id.id})
                if group_id.move_type != "direct":
                    updated_vals.update({"move_type": "direct"})
                if updated_vals:
                    group_id.write(updated_vals)

            values = row._prepare_procurement_values(group_id=group_id)
            product_qty = float(row.qty) - qty

            row_uom = row.uom_id
            quant_uom = row.product_id.uom_id
            product_qty, procurement_uom = row_uom._adjust_uom_quantities(product_qty, quant_uom)
            procurements.append(
                self.env["procurement.group"].Procurement(
                    row.product_id,
                    product_qty,
                    procurement_uom,
                    row.partner_id.property_stock_customer,
                    row.name,
                    row.cycle_id.name,
                    row.company_id,
                    values,
                )
            )
        if procurements:
            self.env["procurement.group"].run(procurements)

        # This next block is currently needed only because the scheduler trigger is done by picking confirmation
        # rather than stock.move confirmation
        cycles = self.mapped("cycle_id")
        for cycle in cycles:
            pickings_to_confirm = cycle.picking_ids.filtered(lambda p: p.state not in ["cancel", "done"])
            if pickings_to_confirm:
                # Trigger the Scheduler for Pickings
                pickings_to_confirm.action_confirm()
        return True
