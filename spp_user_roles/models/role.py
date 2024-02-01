# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResUsersRoleCustomSPP(models.Model):
    _inherit = "res.users.role"

    role_type = fields.Selection([("local", "Local"), ("global", "Global")], default="global")

    @api.onchange("role_type")
    def _onchange_role_type(self):
        for rec in self:
            if rec.role_type == "global":
                rl = rec.line_ids.filtered(lambda a: not a.local_area_id)
                if rl:
                    rl.update({"local_area_id": None})

    def action_update_users(self):
        """
        Call the update_users function to force the update of associated users in the role.
        :return:
        """
        for rec in self:
            logging.info("Update user roles for %s" % rec.name)
            rec.update_users()


class ResUsersRoleLineCustomSPP(models.Model):
    _inherit = "res.users.role.line"

    role_type = fields.Selection(related="role_id.role_type")

    local_area_id = fields.Many2one("spp.area", string="Center Area")
