# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from odoo import models


class ConfirmUserAssignmentWiz(models.TransientModel):
    _inherit = "spp.change.request.user.assign.wizard"

    def _get_group_ids(self):
        """
        Get the group ids for the user.
        Override this method in the implementation-specific module to specify the group ids to be checked.

        :return: List of group ids.
        """
        return [
            self.env.ref("spp_change_request.group_spp_change_request_agent").id,
            self.env.ref("spp_change_request.group_spp_change_request_validator").id,
            self.env.ref("spp_change_request.group_spp_change_request_applicator").id,
            self.env.ref("spp_change_request.group_spp_change_request_administrator").id,
        ]
