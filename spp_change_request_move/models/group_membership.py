from odoo import fields, models


class SPPGroupMembershipMoveTransfer(models.Model):
    _inherit = "spp.change.request.group.members"

    group_move_to_id = fields.Many2one("spp.change.request.move.transfer")
