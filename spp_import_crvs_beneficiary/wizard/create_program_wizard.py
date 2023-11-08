from odoo import api, fields, models

from ..tools import field_onchange


class G2PCreateNewProgramWiz(models.TransientModel):
    _inherit = "g2p.program.create.wizard"

    imported_from_crvs = fields.Boolean("Imported from CRVS")

    @api.onchange("imported_from_crvs")
    def on_imported_from_crvs_change(self):
        field_onchange(self, "imported_from_crvs", "ind_is_imported_from_crvs")

    def _get_default_eligibility_manager_val(self, program_id):
        val = super()._get_default_eligibility_manager_val(program_id)

        val.update(
            {
                "imported_from_crvs": self.imported_from_crvs,
            }
        )

        return val
