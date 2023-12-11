from odoo import api, fields, models


class OpenSPPGroupMembership(models.Model):
    _inherit = "g2p.group.membership"

    is_created_from_crvs = fields.Boolean(
        "Created from CRVS",
        compute="_compute_is_created_from_crvs",
        store=True,
    )

    @api.depends("group")
    def _compute_is_created_from_crvs(self):
        for rec in self:
            rec.is_created_from_crvs = rec.group.grp_is_created_from_crvs
