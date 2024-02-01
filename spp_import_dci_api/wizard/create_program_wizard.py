from odoo import api, fields, models

from ..models.constants import DATA_SOURCE_NAME
from ..tools import field_onchange


class G2PCreateNewProgramWiz(models.TransientModel):
    _inherit = "g2p.program.create.wizard"

    data_source_id = fields.Many2one("spp.data.source")
    location_id = fields.Many2one("spp.crvs.location")
    is_crvs_data_source = fields.Boolean()

    @api.onchange("data_source_id")
    def onchange_data_source_id(self):
        field_onchange(self, "data_source_id.name", "data_source_id.name")
        if self.data_source_id and self.data_source_id.name == DATA_SOURCE_NAME:
            self.is_crvs_data_source = True
        else:
            self.is_crvs_data_source = False

    def _get_default_eligibility_manager_val(self, program_id):
        val = super()._get_default_eligibility_manager_val(program_id)

        val.update(
            {
                "data_source_id": self.data_source_id.id,
                "location_id": self.location_id.id,
                "is_crvs_data_source": self.is_crvs_data_source,
            }
        )

        return val

    @api.onchange("location_id")
    def onchange_location_id(self):
        field_onchange(self, "location_id.name", "child_under_12_birthplace", operator="ilike")
