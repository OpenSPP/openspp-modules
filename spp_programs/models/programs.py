# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import _, models

_logger = logging.getLogger(__name__)


class CustomG2PProgram(models.Model):
    _inherit = "g2p.program"

    def import_eligible_registrants(self, state="draft"):
        eligibility_managers = self.get_managers(self.MANAGER_ELIGIBILITY)
        if eligibility_managers:
            manager = eligibility_managers[0]

            domain = manager._prepare_eligible_domain()

            new_beneficiaries = self.env["res.partner"].search(domain)

            # Exclude already added beneficiaries
            beneficiary_ids = self.get_beneficiaries().mapped("partner_id")
            new_beneficiaries = new_beneficiaries - beneficiary_ids

            new_beneficiaries_count = len(new_beneficiaries)

            if new_beneficiaries_count < 1000:
                message = _("%s Imported Beneficiaries") % new_beneficiaries_count
                kind = "success"
            else:
                message = (
                    _("Started importing %s beneficiaries") % new_beneficiaries_count
                )
                kind = "warning"

            manager.import_eligible_registrants()
        else:
            message = _("No Eligibility Manager defined.")
            kind = "danger"

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Import"),
                "message": message,
                "sticky": True,
                "type": kind,
                "next": {
                    "type": "ir.actions.act_window_close",
                },
            },
        }
