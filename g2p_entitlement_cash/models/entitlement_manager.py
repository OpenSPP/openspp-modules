# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class EntitlementManager(models.Model):
    _inherit = "g2p.program.entitlement.manager"
    _description = "Cash Entitlement Manager"

    @api.model
    def _selection_manager_ref_id(self):
        selection = super()._selection_manager_ref_id()
        new_manager = ("g2p.program.entitlement.manager.cash", "Cash")
        if new_manager not in selection:
            selection.append(new_manager)
        return selection


class G2PCashEntitlementManager(models.Model):
    _name = "g2p.program.entitlement.manager.cash"
    _inherit = [
        "g2p.base.program.entitlement.manager",
        "g2p.manager.source.mixin",
    ]
    _description = "Cash Entitlement Manager"

    # Cash Entitlement Manager
    evaluate_one_item = fields.Boolean(default=False)
    entitlement_item_ids = fields.One2many(
        "g2p.program.entitlement.manager.cash.item",
        "entitlement_id",
        "Entitlement Items",
    )
    max_amount = fields.Monetary(
        string="Maximum Amount",
        currency_field="currency_id",
        default=0.0,
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="program_id.journal_id.currency_id",
        readonly=True,
    )

    # Group able to validate the payment
    # Todo: Create a record rule for payment_validation_group
    entitlement_validation_group_id = fields.Many2one(
        "res.groups", string="Entitlement Validation Group"
    )

    def prepare_entitlements(self, cycle, beneficiaries):
        if not self.entitlement_item_ids:
            raise UserError(
                _("There are no items entered for this entitlement manager.")
            )

        all_beneficiaries_ids = beneficiaries.mapped("partner_id.id")

        new_entitlements_to_create = {}
        for rec in self.entitlement_item_ids:
            if rec.condition:
                # Filter res.partner based on entitlement condition and get ids
                domain = [("id", "in", all_beneficiaries_ids)]
                domain += self._safe_eval(rec.condition)
                beneficiaries_ids = self.env["res.partner"].search(domain).ids
                # Check if single evaluation
                if self.evaluate_one_item:
                    # Remove beneficiaries_ids from all_beneficiaries_ids
                    for bid in beneficiaries_ids:
                        if bid in all_beneficiaries_ids:
                            all_beneficiaries_ids.remove(bid)
            else:
                beneficiaries_ids = all_beneficiaries_ids

            beneficiaries_with_entitlements = (
                self.env["g2p.entitlement"]
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
            entitlement_currency = rec.currency_id.id

            beneficiaries_with_entitlements_to_create = self.env["res.partner"].browse(
                entitlements_to_create
            )

            for beneficiary_id in beneficiaries_with_entitlements_to_create:
                if rec.multiplier_field:
                    # Get the multiplier value from multiplier_field else return the default multiplier=1
                    multiplier = beneficiary_id.mapped(rec.multiplier_field.name)
                    if multiplier:
                        multiplier = multiplier[0] or 0
                else:
                    multiplier = 1
                if rec.max_multiplier > 0 and multiplier > rec.max_multiplier:
                    multiplier = rec.max_multiplier
                amount = rec.amount * float(multiplier)

                # Compute the sum of cash entitlements
                if beneficiary_id.id in new_entitlements_to_create:
                    amount = (
                        amount
                        + new_entitlements_to_create[beneficiary_id.id][
                            "initial_amount"
                        ]
                    )
                # Check if amount > max_amount; ignore if max_amount is set to 0
                if self.max_amount > 0.0:
                    if amount > self.max_amount:
                        amount = self.max_amount

                new_entitlements_to_create[beneficiary_id.id] = {
                    "cycle_id": cycle.id,
                    "partner_id": beneficiary_id.id,
                    "initial_amount": amount,
                    "currency_id": entitlement_currency,
                    "state": "draft",
                    "is_cash_entitlement": True,
                    "valid_from": entitlement_start_validity,
                    "valid_until": entitlement_end_validity,
                }

        # Create entitlement records
        for ent in new_entitlements_to_create:
            initial_amount = new_entitlements_to_create[ent]["initial_amount"]
            new_entitlements_to_create[ent]["initial_amount"] = self._check_subsidy(
                initial_amount
            )
            # Create non-zero entitlements only
            if new_entitlements_to_create[ent]["initial_amount"] > 0.0:
                self.env["g2p.entitlement"].create(new_entitlements_to_create[ent])

    def _check_subsidy(self, amount):
        # Check if initial_amount < max_amount then set = max_amount
        # Ignore if max_amount is set to 0
        if self.max_amount > 0.0:
            if amount < self.max_amount:
                return self.max_amount
        return amount

    def validate_entitlements(self, cycle, cycle_memberships):
        # TODO: Change the status of the entitlements to `validated` for this members.
        # move the funds from the program's wallet to the wallet of each Beneficiary that are validated
        pass

    def is_cash_entitlement(self):
        return True

    def approve_entitlements(self, entitlements):
        amt = 0.0
        state_err = 0
        message = ""
        sw = 0
        for rec in entitlements:
            if rec.state in ("draft", "pending_validation"):
                fund_balance = self.check_fund_balance(rec.cycle_id.program_id.id) - amt
                if fund_balance >= rec.initial_amount:
                    amt += rec.initial_amount
                    # Prepare journal entry (account.move) via account.payment
                    amount = rec.initial_amount
                    new_service_fee = None
                    if rec.transfer_fee > 0.0:
                        amount -= rec.transfer_fee
                        # Incurred Fees (transfer fees)
                        payment = {
                            "partner_id": rec.partner_id.id,
                            "payment_type": "outbound",
                            "amount": rec.transfer_fee,
                            "currency_id": rec.journal_id.currency_id.id,
                            "journal_id": rec.journal_id.id,
                            "partner_type": "supplier",
                            "ref": "Service Fee: Code: %s" % rec.code,
                        }
                        new_service_fee = self.env["account.payment"].create(payment)

                    # Fund Disbursed (amount - transfer fees)
                    payment = {
                        "partner_id": rec.partner_id.id,
                        "payment_type": "outbound",
                        "amount": amount,
                        "currency_id": rec.journal_id.currency_id.id,
                        "journal_id": rec.journal_id.id,
                        "partner_type": "supplier",
                        "ref": "Fund disbursed to beneficiary: Code: %s" % rec.code,
                    }
                    new_payment = self.env["account.payment"].create(payment)

                    rec.update(
                        {
                            "disbursement_id": new_payment.id,
                            "service_fee_disbursement_id": new_service_fee
                            and new_service_fee.id
                            or None,
                            "state": "approved",
                            "date_approved": fields.Date.today(),
                        }
                    )
                else:
                    raise UserError(
                        _(
                            "The fund for the program: %(program)s [%(fund).2f] "
                            + "is insufficient for the entitlement: %(entitlement)s"
                        )
                        % {
                            "program": rec.cycle_id.program_id.name,
                            "fund": fund_balance,
                            "entitlement": rec.code,
                        }
                    )

            else:
                state_err += 1
                if sw == 0:
                    sw = 1
                    message = _(
                        "<b>Entitlement State Error! Entitlements not in 'pending validation' state:</b>\n"
                    )
                message += _("Program: %(prg)s, Beneficiary: %(partner)s.\n") % {
                    "prg": rec.cycle_id.program_id.name,
                    "partner": rec.partner_id.name,
                }

        return (state_err, message)

    def open_entitlement_form(self, rec):
        return {
            "name": "Cash Entitlement",
            "view_mode": "form",
            "res_model": "g2p.entitlement",
            "res_id": rec.id,
            "view_id": self.env.ref("g2p_programs.view_entitlement_form").id,
            "type": "ir.actions.act_window",
            "target": "new",
        }


class G2PCashEntitlementItem(models.Model):
    _name = "g2p.program.entitlement.manager.cash.item"
    _description = "Cash Entitlement Manager Items"
    _order = "sequence,id"

    sequence = fields.Integer(default=1000)
    entitlement_id = fields.Many2one(
        "g2p.program.entitlement.manager.cash", "Cash Entitlement", required=True
    )

    amount = fields.Monetary(
        currency_field="currency_id",
        group_operator="sum",
        default=0.0,
        string="Amount per cycle",
        required=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="entitlement_id.program_id.journal_id.currency_id",
        readonly=True,
    )

    # non-mandatory field to store a domain that is used to verify if this item is valid for a beneficiary
    # For example, it could be: [('is_woman_headed_household, '=', True)]
    # If the condition is not met, this calculation is not used
    condition = fields.Char("Condition Domain")

    # `multiplier_field` can be any integer field of `res.partner`
    # It could be the number of members, children, elderly, or any other metrics.
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
