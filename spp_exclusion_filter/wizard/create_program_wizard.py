import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class CustomSPPCreateNewProgramWiz(models.TransientModel):
    _inherit = "g2p.program.create.wizard"

    enable_exclusion_filter = fields.Boolean("Enable Exclusion")
    exclusion_eligibility_domain = fields.Text(
        string="Exclusive Domain", default="[]", required=True, copy=False
    )

    def _create_default_eligibility_manager(self, program_id):
        def_mgr = super()._create_default_eligibility_manager(program_id)
        if self.eligibility_kind == "default_eligibility":
            def_mgr.enable_exclusion_filter = self.enable_exclusion_filter
            def_mgr.exclusion_eligibility_domain = self.exclusion_eligibility_domain

        return def_mgr
