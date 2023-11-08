import logging

from odoo import api, fields, models

from ..tools import field_onchange

_logger = logging.getLogger(__name__)


class SPPDefaultEligibilityManager(models.Model):
    _inherit = "g2p.program_membership.manager.default"

    imported_from_crvs = fields.Boolean("Imported from CRVS")

    @api.onchange("imported_from_crvs")
    def on_imported_from_crvs_change(self):
        field_onchange(self, "imported_from_crvs", "ind_is_imported_from_crvs")
