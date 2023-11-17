from odoo import api, fields, models

from ..tools import field_onchange


class G2PCreateNewProgramWiz(models.TransientModel):
    _inherit = "g2p.program.create.wizard"

    data_source_id = fields.Many2one("spp.data.source")

    @api.onchange("data_source_id")
    def onchange_data_source_id(self):
        field_onchange(self, "data_source_id.name", "data_source_id.name")

    def _get_default_eligibility_manager_val(self, program_id):
        val = super()._get_default_eligibility_manager_val(program_id)

        val.update(
            {
                "data_source_id": self.data_source_id,
            }
        )

        return val
