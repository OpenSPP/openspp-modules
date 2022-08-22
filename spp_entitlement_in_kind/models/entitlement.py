# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


class G2PInKindEntitlement(models.Model):
    _inherit = "g2p.entitlement"

    product_id = fields.Many2one(
        "product.product", "Product", domain=[("type", "=", "product")]
    )
    qty = fields.Integer("QTY", default=1)
    uom_id = fields.Many2one("uom.uom", "Unit of Measure")
    inkind_item_id = fields.Many2one(
        "g2p.program.entitlement.manager.inkind.item", "In-Kind Entitlement Condition"
    )

    # Inventory integration fields
    manage_inventory = fields.Boolean(default=False)
    warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Warehouse",
    )
    route_id = fields.Many2one(
        "stock.location.route", string="Route", ondelete="restrict", check_company=True
    )
    move_ids = fields.One2many("stock.move", "entitlement_id", string="Stock Moves")

    def _compute_name(self):
        for record in self:
            name = _("Entitlement")
            if record.is_cash_entitlement:
                initial_amount = "{:,.2f}".format(record.initial_amount)
                name += (
                    " Cash ["
                    + str(record.currency_id.symbol)
                    + " "
                    + initial_amount
                    + "]"
                )
            else:
                name += ": In-Kind (" + record.product_id.name + ")"
            record.name = name

    def approve_entitlement(self):
        amt = 0.0
        state_err = 0
        sw = 0
        for rec in self:
            if rec.state in ("draft", "pending_validation"):
                if rec.is_cash_entitlement:
                    fund_balance = (
                        self.check_fund_balance(rec.cycle_id.program_id.id) - amt
                    )
                    if fund_balance >= rec.initial_amount:
                        amt += rec.initial_amount
                        # Prepare journal entry (account.move) via account.payment
                        payment = {
                            "partner_id": rec.partner_id.id,
                            "payment_type": "outbound",
                            "amount": rec.initial_amount,
                            "currency_id": rec.journal_id.currency_id.id,
                            "journal_id": rec.journal_id.id,
                            "partner_type": "supplier",
                        }
                        new_payment = self.env["account.payment"].create(payment)
                        rec.update(
                            {
                                "disbursement_id": new_payment.id,
                                "state": "approved",
                                "date_approved": fields.Date.today(),
                            }
                        )
                    else:
                        raise UserError(
                            _(
                                "The fund for the program: %(program)s[%(fund).2f] "
                                + "is insufficient for the entitlement: %(entitlement)s"
                            )
                            % {
                                "program": rec.cycle_id.program_id.name,
                                "fund": fund_balance,
                                "entitlement": rec.code,
                            }
                        )
                else:  # In-Kind Entitlements
                    if rec.manage_inventory:
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
                        "<b>Entitle State Error! Entitlements not in 'pending validation' state:</b>\n"
                    )
                message += _("Program: %(program)s, Beneficiary: %(partner)s.\n") % {
                    "program": rec.cycle_id.program_id.name,
                    "partner": rec.partner_id.name,
                }

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
                },
            }

    def open_entitlement_form(self):
        if self.is_cash_entitlement:
            view = "g2p_programs.view_entitlement_form"
        else:  # In-kind Entitlement
            view = "g2p_entitlement_in_kind.view_entitlement_inkind_form"
        return {
            "name": "Entitlement",
            "view_mode": "form",
            "res_model": "g2p.entitlement",
            "res_id": self.id,
            "view_id": self.env.ref(view).id,
            "type": "ir.actions.act_window",
            "target": "new",
        }

    # Inventory functions
    def _prepare_procurement_values(self, group_id=False):
        """Prepare specific key for moves or other components that will be created from a stock rule
        comming from an entitlement.
        """
        self.ensure_one()
        # Use the delivery date if there is else use date_order and lead time
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
            qty += move.product_uom._compute_quantity(
                move.product_uom_qty, self.uom_id, rounding_method="HALF-UP"
            )
        for move in incoming_moves:
            qty -= move.product_uom._compute_quantity(
                move.product_uom_qty, self.uom_id, rounding_method="HALF-UP"
            )
        return qty

    def _get_outgoing_incoming_moves(self):
        outgoing_moves = self.env["stock.move"]
        incoming_moves = self.env["stock.move"]

        moves = self.move_ids.filtered(
            lambda r: r.state != "cancel"
            and not r.scrapped
            and self.product_id == r.product_id
        )

        for move in moves:
            if move.location_dest_id.usage == "customer":
                if not move.origin_returned_move_id or (
                    move.origin_returned_move_id and move.to_refund
                ):
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
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
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
                group_id = self.env["procurement.group"].create(
                    row._prepare_procurement_group_vals()
                )
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
            product_qty, procurement_uom = row_uom._adjust_uom_quantities(
                product_qty, quant_uom
            )
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
            pickings_to_confirm = cycle.picking_ids.filtered(
                lambda p: p.state not in ["cancel", "done"]
            )
            if pickings_to_confirm:
                # Trigger the Scheduler for Pickings
                pickings_to_confirm.action_confirm()
        return True
