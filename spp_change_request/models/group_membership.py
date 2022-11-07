from odoo import fields, models


class SPPGroupMembershipTemp(models.Model):
    _name = "spp.change.request.group.members"
    _description = "Group Membership"
    _order = "id desc"

    group_add_children_id = fields.Many2one("spp.change.request.add.children")
    individual_id = fields.Many2one("res.partner", string="Registrant")
    kind_ids = fields.Many2many("g2p.group.membership.kind", string="Membership Types")
    start_date = fields.Datetime(default=lambda self: fields.Datetime.now())
    end_date = fields.Datetime()
    birthdate = fields.Date("Date of Birth", related="individual_id.birthdate")
    age = fields.Char(related="individual_id.age")
