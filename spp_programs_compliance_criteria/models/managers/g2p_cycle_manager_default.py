from odoo import models
from odoo.osv.expression import AND


class G2pCycleManagerDefault(models.Model):
    _inherit = "g2p.cycle.manager.default"

    def _add_beneficiaries(self, cycle, beneficiaries, state="draft", do_count=False):
        automated_beneficiaries_filtering_mechanism = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "spp_programs_compliance_criteria.beneficiaries_automated_filtering_mechanism",
                "0",
            )
        )
        if automated_beneficiaries_filtering_mechanism == "1" and cycle.program_id.compliance_managers:
            domain = cycle._get_compliance_criteria_domain()
            new_domain = AND([domain, [["id", "in", beneficiaries]]])
            beneficiaries = self.env["res.partner"].sudo().search(new_domain).ids
        res = super()._add_beneficiaries(cycle, beneficiaries, state, do_count)
        return res
