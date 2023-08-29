# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class G2PCashEntitlementManagerCustomSP(models.Model):
    """
    G2PCashEntitlementManagerCustomSP adds the management of service points in
    generating entitlements using the cash entitlement manager.

    If the value of store_sp_in_entitlements in g2p.programs is True, then all generated entitlements
    must store the beneficiaries service points.

    """

    _inherit = "g2p.program.entitlement.manager.cash"

    def prepare_entitlements(self, cycle, beneficiaries):
        """Prepare Cash Entitlements.
        This overrides the Cash Entitlement Manager :meth:`prepare_entitlements`
        to support the storing of service points in the generated entitlements.

        :param cycle: The cycle.
        :param beneficiaries: The beneficiaries.
        :return:
        """
        if not self.entitlement_item_ids:
            raise UserError(
                _("There are no items entered for this entitlement manager.")
            )

        # Check if service points needs to be added in the entitlements
        use_service_point_ids = False
        if cycle.program_id.store_sp_in_entitlements:
            use_service_point_ids = True

        all_beneficiaries_ids = beneficiaries.mapped("partner_id.id")

        new_entitlements_to_create = {}
        for rec in self.entitlement_item_ids:
            if rec.condition:
                beneficiaries_ids = self._get_all_beneficiaries(
                    all_beneficiaries_ids, rec.condition, self.evaluate_one_item
                )
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

                # Get the beneficiarie's service points
                if use_service_point_ids:
                    service_point_ids = beneficiary_id.service_point_ids or None
                else:
                    service_point_ids = None

                new_entitlements_to_create[beneficiary_id.id] = {
                    "cycle_id": cycle.id,
                    "partner_id": beneficiary_id.id,
                    "initial_amount": amount,
                    "currency_id": entitlement_currency,
                    "state": "draft",
                    "is_cash_entitlement": True,
                    "valid_from": entitlement_start_validity,
                    "valid_until": entitlement_end_validity,
                    # Add the service points to the entitlement
                    "service_point_ids": service_point_ids,
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
