import logging

from odoo import api, fields, models

from ..tools import field_onchange

_logger = logging.getLogger(__name__)


class SPPDefaultEligibilityManager(models.Model):
    _inherit = "g2p.program_membership.manager.default"

    data_source_id = fields.Many2one("spp.data.source")

    @api.onchange("data_source_id")
    def onchange_data_source_id(self):
        field_onchange(self, "data_source_id.name", "data_source_id.name")
