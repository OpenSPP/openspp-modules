# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResUsersRoleCustomSPP(models.Model):
    _inherit = "res.users.role"

    @api.onchange("role_type")
    def _onchange_role_type(self):
        for rec in self:
            if rec.role_type == "global":
                rl = rec.line_ids.filtered(lambda a: not a.local_area_id)
                if rl:
                    rl.update({"local_area_id": None})


class ResUsersRoleLineCustomSPP(models.Model):
    _inherit = "res.users.role.line"

    local_area_id = fields.Many2one("spp.area", string="Center Area")
