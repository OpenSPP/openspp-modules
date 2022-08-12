# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class EntitlementManager(models.Model):
    _name = "g2p.program.entitlement.manager"
    _description = "Entitlement Manager"
    _inherit = "g2p.manager.mixin"

    program_id = fields.Many2one("g2p.program", "Program")

    @api.model
    def _selection_manager_ref_id(self):
        selection = super()._selection_manager_ref_id()
        new_manager = ("g2p.program.entitlement.manager.default", "Default")
        if new_manager not in selection:
            selection.append(new_manager)
        return selection


class BaseEntitlementManager(models.AbstractModel):
    _name = "g2p.base.program.entitlement.manager"
    _inherit = "base.programs.manager"
    _description = "Base Entitlement Manager"

    name = fields.Char("Manager Name", required=True)
    program_id = fields.Many2one("g2p.program", string="Program", required=True)

    def prepare_entitlements(self, cycle, cycle_memberships):
        """
        This method is used to prepare the entitlement list of the beneficiaries.
        :param cycle: The cycle.
        :param cycle_memberships: The beneficiaries.
        :return:
        """
        raise NotImplementedError()

    def validate_entitlements(self, cycle, cycle_memberships):
        """
        This method is used to validate the entitlement list of the beneficiaries.
        :param cycle: The cycle.
        :param cycle_memberships: The beneficiaries.
        :return:
        """
        raise NotImplementedError()


class DefaultCashEntitlementManager(models.Model):
    _name = "g2p.program.entitlement.manager.default"
    _inherit = ["g2p.base.program.entitlement.manager", "g2p.manager.source.mixin"]
    _description = "Default Entitlement Manager"

    amount_per_cycle = fields.Monetary(
        currency_field="currency_id",
        group_operator="sum",
        default=0.0,
        string="Amount per cycle",
    )
    amount_per_individual_in_group = fields.Monetary(
        currency_field="currency_id",
        group_operator="sum",
        default=0.0,
        string="Amount per individual in group",
    )
    max_individual_in_group = fields.Integer(
        default=0,
        string="Maximum number of individual in group",
        help="0 means no limit",
    )

    currency_id = fields.Many2one(
        "res.currency", related="program_id.journal_id.currency_id", readonly=True
    )

    # Group able to validate the payment
    # Todo: Create a record rule for payment_validation_group
    entitlement_validation_group_id = fields.Many2one(
        "res.groups", string="Entitlement Validation Group"
    )

    def prepare_entitlements(self, cycle, beneficiaries):
        # TODO: create a Entitlement of `amount_per_cycle` for each member that do not have one yet for the cycle and
        benecifiaries_ids = beneficiaries.mapped("partner_id.id")

        benecifiaries_with_entitlements = (
            self.env["g2p.entitlement"]
            .search(
                [("cycle_id", "=", cycle.id), ("partner_id", "in", benecifiaries_ids)]
            )
            .mapped("partner_id.id")
        )
        entitlements_to_create = [
            benecifiaries_id
            for benecifiaries_id in benecifiaries_ids
            if benecifiaries_id not in benecifiaries_with_entitlements
        ]

        entitlement_start_validity = cycle.start_date
        entitlement_end_validity = cycle.end_date
        entitlement_currency = self.currency_id.id

        beneficiaries_with_entitlements_to_create = self.env["res.partner"].browse(
            entitlements_to_create
        )

        for beneficiary_id in beneficiaries_with_entitlements_to_create:
            self.env["g2p.entitlement"].create(
                {
                    "cycle_id": cycle.id,
                    "partner_id": beneficiary_id.id,
                    "initial_amount": self._calculate_amount(beneficiary_id),
                    "currency_id": entitlement_currency,
                    "state": "draft",
                    "is_cash_entitlement": True,
                    "valid_from": entitlement_start_validity,
                    "valid_until": entitlement_end_validity,
                }
            )

    def _calculate_amount(self, beneficiary):
        total = self.amount_per_cycle
        if beneficiary.is_group:
            num_individuals = beneficiary.count_individuals()
            if (
                self.max_individual_in_group
                and num_individuals > self.max_individual_in_group
            ):
                num_individuals = self.max_individual_in_group
            total += self.amount_per_individual_in_group * num_individuals
        return total

    def validate_entitlements(self, cycle, cycle_memberships):
        # TODO: Change the status of the entitlements to `validated` for this members.
        # move the funds from the program's wallet to the wallet of each Beneficiary that are validated
        pass
