# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class G2PDefaultEntitlementManagerCustomSP(models.Model):
    """
    G2PDefaultEntitlementManagerCustomSP adds the management of service points in
    generating entitlements using the default entitlement manager.

    If the value of store_sp_in_entitlements in g2p.programs is True, then all generated entitlements
    must store the beneficiaries service points.

    """

    _inherit = "g2p.program.entitlement.manager.default"

    def prepare_entitlements(self, cycle, beneficiaries):
        """Prepare entitlements.
        This overrides the Default Entitlement Manager :meth:`prepare_entitlements`
        to support the storing of service points in the generated entitlements.
        :param cycle: The cycle.
        :param beneficiaries: The beneficiaries.
        :return:
        """
        # Check if service points needs to be added in the entitlements
        use_service_point_ids = False
        if cycle.program_id.store_sp_in_entitlements:
            use_service_point_ids = True

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

        individual_count = beneficiaries_with_entitlements_to_create.count_individuals()
        individual_count_map = dict(individual_count)

        entitlements = []
        for beneficiary_id in beneficiaries_with_entitlements_to_create:
            amount = self._calculate_amount(
                beneficiary_id, individual_count_map.get(beneficiary_id.id, 0)
            )
            transfer_fee = 0.0
            if self.transfer_fee_pct > 0.0:
                transfer_fee = amount * (self.transfer_fee_pct / 100.0)
            elif self.transfer_fee_amt > 0.0:
                transfer_fee = self.transfer_fee_amt

            # Get the beneficiarie's service points
            if use_service_point_ids:
                service_point_ids = beneficiary_id.service_point_ids or None
            else:
                service_point_ids = None

            entitlements.append(
                {
                    "cycle_id": cycle.id,
                    "partner_id": beneficiary_id.id,
                    "initial_amount": amount,
                    "transfer_fee": transfer_fee,
                    "currency_id": entitlement_currency,
                    "state": "draft",
                    "is_cash_entitlement": True,
                    "valid_from": entitlement_start_validity,
                    "valid_until": entitlement_end_validity,
                    # Add the service points to the entitlement
                    "service_point_ids": service_point_ids,
                }
            )
        if entitlements:
            self.env["g2p.entitlement"].create(entitlements)
