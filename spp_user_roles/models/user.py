# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import Command, api, fields, models


class ResUsersCustomSPP(models.Model):
    _inherit = "res.users"

    center_area_ids = fields.Many2many(
        comodel_name="spp.area",
        string="Center Areas",
        compute="_compute_center_area_ids",
        compute_sudo=True,
    )

    @api.depends("role_line_ids.role_id")
    def _compute_center_area_ids(self):
        for user in self:
            if user.center_area_ids:
                user.update({"center_area_ids": [Command.clear()]})
            if user.role_line_ids:
                center_area_ids = []
                for rl in user.role_line_ids.filtered(lambda a: a.role_type == "local"):
                    if rl.local_area_id:
                        center_area_ids.append(Command.link(rl.local_area_id.id))
                if center_area_ids:
                    user.update({"center_area_ids": center_area_ids})

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
