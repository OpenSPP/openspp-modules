from odoo import fields, models


class SPPGroupMembership(models.Model):
    _inherit = "spp.change.request.group.members"

    group_add_children_id = fields.Many2one("spp.change.request.add.children")
