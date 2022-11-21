from odoo import fields, models


class SPPGroupMembershipTemp(models.Model):
    _name = "spp.change.request.group.members"
    _description = "Group Membership"
    _order = "id desc"

    individual_id = fields.Many2one("res.partner", string="Registrant")
    kind_ids = fields.Many2many("g2p.group.membership.kind", string="Membership Types")
    start_date = fields.Datetime(default=lambda self: fields.Datetime.now())
    end_date = fields.Datetime()
    birthdate = fields.Date("Date of Birth", related="individual_id.birthdate")
    age = fields.Char(related="individual_id.age")
    phone = fields.Char(string="Phone Numbers", related="individual_id.phone")

    def open_individual_form(self):
        context = {
            "default_is_group": False,
            "create": False,
            "edit": False,
        }
        return {
            "name": "Individual Member",
            "view_mode": "form",
            "res_model": "res.partner",
            "res_id": self.individual_id.id,
            "view_id": self.env.ref("g2p_registry_individual.view_individuals_form").id,
            "type": "ir.actions.act_window",
            "target": "new",
            "context": context,
            "flags": {"mode": "readonly"},
        }
