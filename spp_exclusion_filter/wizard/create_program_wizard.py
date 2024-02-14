import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class CustomSPPCreateNewProgramWiz(models.TransientModel):
    _inherit = "g2p.program.create.wizard"

    enable_exclusion_filter = fields.Boolean("Enable Exclusion")
    exclusion_eligibility_domain = fields.Text(string="Exclusive Domain", default="[]", required=True, copy=False)

    def _get_default_eligibility_manager_val(self, program_id):
        val = super()._get_default_eligibility_manager_val(program_id)

        val.update(
            {
                "enable_exclusion_filter": self.enable_exclusion_filter,
                "exclusion_eligibility_domain": self.exclusion_eligibility_domain,
            }
        )

        return val
