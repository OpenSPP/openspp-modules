# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class CustomDefaultEligibilityManager(models.Model):
    _inherit = "g2p.program_membership.manager.default"

    def import_eligible_registrants(self, state="draft"):
        ben_count = 0
        for rec in self:
            domain = rec._prepare_eligible_domain()
            new_beneficiaries = self.env["res.partner"].search(domain)
            # _logger.debug("Found %s beneficiaries", len(new_beneficiaries))

            # Exclude already added beneficiaries
            beneficiary_ids = rec.program_id.get_beneficiaries().mapped("partner_id")

            # _logger.debug("Excluding %s beneficiaries", len(beneficiary_ids))
            new_beneficiaries = new_beneficiaries - beneficiary_ids
            # _logger.debug("Finally %s beneficiaries", len(new_beneficiaries))

            ben_count = len(new_beneficiaries)
            if ben_count < 1000:
                rec._import_registrants(new_beneficiaries, state=state, do_count=True)
            else:
                rec._import_registrants_async(new_beneficiaries, state=state)

        return ben_count
