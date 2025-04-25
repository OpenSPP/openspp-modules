# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from . import models
from . import controllers

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def _add_farm_constraint(cr, registry):
    """
    Add a CHECK constraint to ensure farm-related fields are NOT NULL only for partners marked as farms.
    This runs after the module installation/update to avoid issues with existing non-farm partners.
    """
    # The registry argument is not strictly needed here, but kept for potential future use
    # or if called directly from other contexts requiring it.
    _logger.info("Attempting to add CHECK constraint 'farm_fields_not_null_if_farm'...")
    cr.execute(
        """
        ALTER TABLE res_partner
        DROP CONSTRAINT IF EXISTS farm_fields_not_null_if_farm;
    """
    )
    cr.execute(
        """
        ALTER TABLE res_partner
        ADD CONSTRAINT farm_fields_not_null_if_farm CHECK (
            (is_farm IS NOT TRUE) -- Allows NULLs if is_farm is False or NULL
            OR
            (farm_detail_id IS NOT NULL AND farm_land_rec_id IS NOT NULL AND farmer_id IS NOT NULL)
        );
    """
    )
    _logger.info("CHECK constraint 'farm_fields_not_null_if_farm' SQL executed.")


def _spp_farmer_registry_base_post_init(env):
    """Post-init hook."""
    _logger.info("Running post-init hook for spp_farmer_registry_base...")
    cr = env.cr
    # Pass the cursor and the env (acting as registry) to the constraint function
    _add_farm_constraint(cr, env)
    _logger.info("Post-init hook for spp_farmer_registry_base finished.")
