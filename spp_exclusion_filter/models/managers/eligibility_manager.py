import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class SPPDefaultEligibilityManager(models.Model):
    _inherit = "g2p.program_membership.manager.default"

    enable_exclusion_filter = fields.Boolean("Enable Exclusion")
    exclusion_eligibility_domain = fields.Text(string="Exclusive Domain", default="[]", required=True)

    def _prepare_exclusion_eligible_domain(self):
        domain = []

        # Do not include disabled registrants
        domain += [("disabled", "=", False)]
        # TODO: use the config of the program
        if self.program_id.target_type == "group":
            domain += [("is_group", "=", True)]
        if self.program_id.target_type == "individual":
            domain += [("is_group", "=", False)]
        domain += self._safe_eval(self.exclusion_eligibility_domain)
        return domain

    def import_eligible_registrants(self, state="draft"):
        for rec in self:
            domain = rec._prepare_eligible_domain()
            new_beneficiaries = self.env["res.partner"].search(domain)

            if rec.enable_exclusion_filter:
                exclusive_domain = rec._prepare_exclusion_eligible_domain()
                excluded_beneficiaries = self.env["res.partner"].search(exclusive_domain)

                new_beneficiaries = new_beneficiaries - excluded_beneficiaries

            # Exclude already added beneficiaries
            beneficiary_ids = rec.program_id.get_beneficiaries().mapped("partner_id")

            new_beneficiaries = new_beneficiaries - beneficiary_ids

            ben_count = len(new_beneficiaries)

            if len(new_beneficiaries) < 1000:
                rec._import_registrants(new_beneficiaries, state=state, do_count=True)
            else:
                rec._import_registrants_async(new_beneficiaries, state=state)

            return ben_count
