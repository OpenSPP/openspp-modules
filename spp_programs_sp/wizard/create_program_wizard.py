# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import fields, models

# from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SPPCreateNewProgramWiz(models.TransientModel):
    _inherit = "g2p.program.create.wizard"

    # Store beneficiary service points in entitlements
    store_sp_in_entitlements = fields.Boolean("Store Service Points to Entitlements")

    def create_g2p_program(self):
        # Create a new journal for this program
        journal_id = self.create_journal(self.name, self.currency_id.id)

        return self.env["g2p.program"].create(
            {
                "name": self.name,
                "journal_id": journal_id,
                "target_type": self.target_type,
                # Add the store_sp_in_entitlements field in program module
                "store_sp_in_entitlements": self.store_sp_in_entitlements,
            }
        )
