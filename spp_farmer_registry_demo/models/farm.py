from odoo import _, fields, models
from odoo.exceptions import UserError


class Farm(models.Model):
    _inherit = "res.partner"

    household_size = fields.Integer()


class FarmGroupMembership(models.Model):
    _inherit = "g2p.group.membership"

    def open_member_form(self):
        for rec in self:
            if rec.individual:
                if rec.individual.is_group:
                    return {
                        "name": "Group Membership",
                        "view_mode": "form",
                        "res_model": "res.partner",
                        "res_id": rec.individual.id,
                        "view_id": self.env.ref("g2p_registry_group.view_groups_form").id,
                        "type": "ir.actions.act_window",
                        "target": "new",
                        "context": {"default_is_group": True},
                        "flags": {"mode": "readonly"},
                    }
                else:
                    return rec.open_individual_form()
            else:
                raise UserError(_("A group or individual must be specified for this member."))
