# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class G2PDefaultEntitlementManagerCustom(models.Model):
    """
    G2PDefaultEntitlementManagerCustom adds the configured card number in
    generating entitlements using the default entitlement manager.

    If the value of id_type in the entitlement manager is set, then all generated entitlements
    will store the beneficiaries card number (configured card type in entitlement manager).

    """

    _inherit = "g2p.program.entitlement.manager.default"

    def prepare_entitlements(self, cycle, beneficiaries):
        """Prepare entitlements.
        This overrides the Default Entitlement Manager :meth:`prepare_entitlements`
        to support the storing of additional fields in the generated entitlements.
        :param cycle: The cycle.
        :param beneficiaries: The beneficiaries.
        :return:
        """
        benecifiaries_ids = beneficiaries.mapped("partner_id.id")

        benecifiaries_with_entitlements = (
            self.env["g2p.entitlement"]
            .search([("cycle_id", "=", cycle.id), ("partner_id", "in", benecifiaries_ids)])
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

        beneficiaries_with_entitlements_to_create = self.env["res.partner"].browse(entitlements_to_create)

        individual_count = beneficiaries_with_entitlements_to_create.count_individuals()
        individual_count_map = dict(individual_count)

        entitlements = []
        for beneficiary_id in beneficiaries_with_entitlements_to_create:
            amount = self._calculate_amount(beneficiary_id, individual_count_map.get(beneficiary_id.id, 0))
            transfer_fee = 0.0
            if self.transfer_fee_pct > 0.0:
                transfer_fee = amount * (self.transfer_fee_pct / 100.0)
            elif self.transfer_fee_amt > 0.0:
                transfer_fee = self.transfer_fee_amt

            entitlement_fields = {
                "cycle_id": cycle.id,
                "partner_id": beneficiary_id.id,
                "initial_amount": amount,
                "transfer_fee": transfer_fee,
                "currency_id": entitlement_currency,
                "state": "draft",
                "is_cash_entitlement": True,
                "valid_from": entitlement_start_validity,
                "valid_until": entitlement_end_validity,
            }
            # Check if there are additional fields to be added in entitlements
            addl_fields = self._get_addl_entitlement_fields(beneficiary_id)
            if addl_fields:
                entitlement_fields.update(addl_fields)
            entitlements.append(entitlement_fields)

        if entitlements:
            self.env["g2p.entitlement"].create(entitlements)

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
