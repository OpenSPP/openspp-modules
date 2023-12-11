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

    def _get_addl_entitlement_fields(self, beneficiary_id):
        """
        Extends this function to include the service_point_ids if enabled in the program configuration.
        Add the service_point_ids of the beneficiaries based on the program config.
        """
        retval = super()._get_addl_entitlement_fields(beneficiary_id)
        # Check if service points needs to be added in the entitlements
        use_service_point_ids = False
        if self.program_id.store_sp_in_entitlements:
            use_service_point_ids = True

        # Get the beneficiarie's service points
        if use_service_point_ids:
            service_point_ids = beneficiary_id.service_point_ids or None
        else:
            service_point_ids = None

        # Add the service points to the entitlement
        if retval:
            retval.update(
                {
                    "service_point_ids": service_point_ids,
                }
            )
        else:
            retval = {
                "service_point_ids": service_point_ids,
            }
        return retval
