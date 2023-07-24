# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class ResUsersCustomSPP(models.Model):
    _inherit = "res.users"

    @api.model
    def _default_role_lines(self):
        default_user = self.env.ref("base.default_user", raise_if_not_found=False)
        default_values = []
        if default_user:
            for role_line in default_user.with_context(active_test=False).role_line_ids:
                default_values.append(
                    {
                        "role_id": role_line.role_id.id,
                        "date_from": role_line.date_from,
                        "date_to": role_line.date_to,
                        "is_enabled": role_line.is_enabled,
                        "local_area_id": role_line.local_area_id.id,
                    }
                )
        return default_values
