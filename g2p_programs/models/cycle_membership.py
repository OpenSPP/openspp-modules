# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class G2PCycleMembership(models.Model):
    _inherit = ["mail.thread", "mail.activity.mixin"]
    # TODO: rename "g2p.cycle.membership" to "g2p.cycle.beneficiaries"
    _name = "g2p.cycle.membership"
    _description = "Cycle Membership"
    _order = "id desc"

    partner_id = fields.Many2one(
        "res.partner", "Registrant", help="A beneficiary", required=True
    )
    cycle_id = fields.Many2one("g2p.cycle", "Cycle", help="A cycle", required=True)
    enrollment_date = fields.Date(
        "Enrollment Date", default=lambda self: fields.Datetime.now()
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("enrolled", "Enrolled"),
            ("paused", "Paused"),
            ("exited", "Exited"),
            ("not_eligible", "Not Eligible"),
        ],
        default="draft",
        copy=False,
    )

    _sql_constraints = [
        (
            "cycle_membership_unique",
            "unique (partner_id, cycle_id)",
            "Beneficiary must be unique per cycle.",
        ),
    ]

    def name_get(self):
        res = super(G2PCycleMembership, self).name_get()
        for rec in self:
            name = ""
            if rec.cycle_id:
                name += "[" + rec.cycle_id.name + "] "
            if rec.partner_id:
                name += rec.partner_id.name
            res.append((rec.id, name))
        return res

    def open_cycle_membership_form(self):
        return {
            "name": "Cycle Membership",
            "view_mode": "form",
            "res_model": "g2p.cycle.membership",
            "res_id": self.id,
            "view_id": self.env.ref("g2p_programs.view_cycle_membership_form").id,
            "type": "ir.actions.act_window",
            "target": "new",
        }

    def open_registrant_form(self):
        if self.partner_id.is_group:
            return {
                "name": "Group Member",
                "view_mode": "form",
                "res_model": "res.partner",
                "res_id": self.partner_id.id,
                "view_id": self.env.ref("g2p_registry_group.view_groups_form").id,
                "type": "ir.actions.act_window",
                "target": "new",
                "context": {"default_is_group": True},
                "flags": {"mode": "readonly"},
            }
        else:
            return {
                "name": "Individual Member",
                "view_mode": "form",
                "res_model": "res.partner",
                "res_id": self.partner_id.id,
                "view_id": self.env.ref(
                    "g2p_registry_individual.view_individuals_form"
                ).id,
                "type": "ir.actions.act_window",
                "target": "new",
                "context": {"default_is_group": False},
                "flags": {"mode": "readonly"},
            }
