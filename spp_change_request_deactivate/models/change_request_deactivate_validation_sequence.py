# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class ChangeRequestDeactivateValidationSequence(models.Model):
    _inherit = "spp.change.request.validation.sequence"

    @api.model
    def _selection_request_type_ref_id(self):
        selection = super()._selection_request_type_ref_id()
        new_request_type = ("spp.change.request.deactivate", "Deactivate Members")
        if new_request_type not in selection:
            selection.append(new_request_type)
        return selection
