from odoo import fields, models


class SPPGroupMembershipSplit(models.Model):
    _inherit = "spp.change.request.group.members"

    group_to_split_id = fields.Many2one("spp.change.request.split")
