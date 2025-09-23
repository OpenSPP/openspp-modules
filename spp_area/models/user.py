# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import Command, api, fields, models


class SPPUserCustom(models.Model):
    _inherit = "res.users"

    center_area_ids = fields.Many2many(
        comodel_name="spp.area",
        string="Center Areas",
        compute="_compute_center_area_ids",
        store=True,
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
        default_values = super()._default_role_lines()

        default_user = self.env.ref("base.default_user", raise_if_not_found=False)
        for default_value in default_values:
            for role_line in default_user.with_context(active_test=False).role_line_ids:
                if role_line.role_id.id == default_value["role_id"]:
                    default_value["local_area_id"] = role_line.local_area_id.id
                    break
        return default_values
