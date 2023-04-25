from odoo import fields, models


class SPPGroupMembership(models.Model):
    _inherit = "spp.change.request.group.members"

    group_add_child_id = fields.Many2one("spp.change.request.add.child")
    group_add_member_child_id = fields.Many2one("spp.change.request.add.member.child")
