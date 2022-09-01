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
    one_time_subsidy = fields.Monetary(
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
                # Check if amount > one_time_subsidy; ignore if one_time_subsidy is set to 0
                if self.one_time_subsidy > 0.0:
                    if amount > self.one_time_subsidy:
                        amount = self.one_time_subsidy

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
        # Check if initial_amount < one_time_subsidy then set = one_time_subsidy
        # Ignore if one_time_subsidy is set to 0
        if self.one_time_subsidy > 0.0:
            if amount < self.one_time_subsidy:
                return self.one_time_subsidy
        return amount

    def validate_entitlements(self, cycle, cycle_memberships):
        # TODO: Change the status of the entitlements to `validated` for this members.
        # move the funds from the program's wallet to the wallet of each Beneficiary that are validated
        pass


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
