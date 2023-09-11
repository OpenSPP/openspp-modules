# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import fields, models

# from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SPPCreateNewProgramWiz(models.TransientModel):
    _inherit = "g2p.program.create.wizard"

    # Store beneficiary service points in entitlements
    store_sp_in_entitlements = fields.Boolean("Store Service Points to Entitlements")

    def get_program_vals(self):
        vals = super().get_program_vals()
        vals.update(
            {
                # Add the store_sp_in_entitlements field in program module
                "store_sp_in_entitlements": self.store_sp_in_entitlements,
            }
        )
        return vals
