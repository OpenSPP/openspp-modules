# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class G2PInKindEntitlementManagerCustomSP(models.Model):
    """
    G2PInKindEntitlementManagerCustomSP adds the management of service points in
    generating entitlements using the in-kind entitlement manager.

    If the value of store_sp_in_entitlements in g2p.programs is True, then all generated entitlements
    must store the beneficiaries service points.

    """

    _inherit = "g2p.program.entitlement.manager.inkind"

    def prepare_entitlements(self, cycle, beneficiaries):
        """Prepare In-Kind Entitlements.
        This overrides the In-kind Entitlement Manager :meth:`prepare_entitlements`
        to support the storing of service points in the generated entitlements.
        :param cycle: The cycle.
        :param beneficiaries: The beneficiaries.
        :return:
        """
        # Check if service points needs to be added in the entitlements
        use_service_point_ids = False
        if cycle.program_id.store_sp_in_entitlements:
            use_service_point_ids = True

        if not self.entitlement_item_ids:
            raise UserError(
                _("There are no items entered for this entitlement manager.")
            )

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

            beneficiaries_with_entitlements_to_create = self.env["res.partner"].browse(
                entitlements_to_create
            )

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

                # Get the beneficiarie's service points
                if use_service_point_ids:
                    service_point_ids = beneficiary_id.service_point_ids or None
                else:
                    service_point_ids = None

                entitlements.append(
                    {
                        "cycle_id": cycle.id,
                        "partner_id": beneficiary_id.id,
                        "total_amount": rec.product_id.list_price * qty,
                        "product_id": rec.product_id.id,
                        "qty": qty,
                        "unit_price": rec.product_id.list_price,
                        "uom_id": rec.uom_id.id,
                        "manage_inventory": self.manage_inventory,
                        "warehouse_id": self.warehouse_id
                        and self.warehouse_id.id
                        or None,
                        "inkind_item_id": rec.id,
                        "state": "draft",
                        "valid_from": entitlement_start_validity,
                        "valid_until": entitlement_end_validity,
                        # Add the service points to the entitlement
                        "service_point_ids": service_point_ids,
                    }
                )
            if entitlements:
                self.env["g2p.entitlement.inkind"].create(entitlements)
