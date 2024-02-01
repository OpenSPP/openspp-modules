from odoo import models


class G2pProgramEntitlementManagerDefault(models.Model):
    _inherit = ["g2p.program.entitlement.manager.default"]

    def prepare_entitlements(self, cycle, beneficiaries):
        automated_beneficiaries_filtering_mechanism = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "spp_programs_compliance_criteria.beneficiaries_automated_filtering_mechanism",
                "0",
            )
        )
        if automated_beneficiaries_filtering_mechanism == "2" and cycle.program_id.compliance_managers:
            satisfied_registrant_ids = (
                self.env["res.partner"].sudo().search(cycle._get_compliance_criteria_domain()).ids
            )
            beneficiaries = beneficiaries.filtered(lambda cm: cm.partner_id.id in satisfied_registrant_ids)
        return super().prepare_entitlements(cycle, beneficiaries)
