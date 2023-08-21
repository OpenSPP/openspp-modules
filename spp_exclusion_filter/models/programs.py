# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class CustomG2PProgram(models.Model):
    _inherit = "g2p.program"

    def get_new_beneficiaries(self, manager):
        beneficiaries = super().get_new_beneficiaries(manager)

        if manager.enable_exclusion_filter:
            exclusive_domain = manager._prepare_exclusion_eligible_domain()
            excluded_beneficiaries = self.env["res.partner"].search(exclusive_domain)

            beneficiaries = beneficiaries - excluded_beneficiaries

        return beneficiaries
