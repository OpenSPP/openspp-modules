from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models


class ChangeRequestAddMemberChild(models.Model):
    _name = "spp.change.request.add.member.child"
    _description = "Change Request / Add Member"

    parent_id = fields.Many2one(
        comodel_name="pds.change.request.add.child.member",
        string="Add Member Request",
        ondelete="cascade",
        readonly=True,
    )
    full_name = fields.Char(compute="_compute_full_name")
    given_name = fields.Char("First Name", required=True)
    father_name = fields.Char("Father's Name", required=True)
    grand_father_name = fields.Char("Grand Father's Name", required=True)
    family_name = fields.Char("Last Name")
    birth_place = fields.Char()
    birthdate = fields.Date("Date of Birth", required=True)
    age = fields.Integer(compute="_compute_calc_age", store=True)
    gender = fields.Selection(
        selection=[("Female", "Female"), ("Male", "Male")], required=True
    )
    phone = fields.Char("Phone Number")
    kind = fields.Many2many(
        comodel_name="g2p.group.membership.kind",
        relation="membership_kind_add_member_child_rel",
        string="Group Membership Types",
    )
    relation_to_head = fields.Many2one(
        comodel_name="g2p.relationship",
        string="Relationship to Head",
    )
    applicant_relation = fields.Selection(
        selection=[
            ("father", "Father"),
            ("mother", "Mother"),
            ("grandfather", "Grandfather"),
        ],
        string="Applicant's relation to Child/Member",
    )
    group_member_ids = fields.One2many(
        comodel_name="spp.change.request.group.members",
        inverse_name="group_add_member_child_id",
        string="Group Members",
    )

    @api.depends("given_name", "father_name", "grand_father_name", "family_name")
    def _compute_full_name(self):
        for rec in self:
            full_name = (
                f"{rec.given_name or ''} {rec.father_name or ''}"
                f" {rec.grand_father_name or ''} {rec.family_name or ''}"
            )
            rec.full_name = full_name.title()

    def action_open_self(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _(self._description),
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "context": dict(create=False, edit=False, delete=False),
            "target": "new",
            "flags": {"mode": "readonly"},
        }

    @api.depends("birthdate")
    def _compute_calc_age(self):
        for rec in self:
            rec.age = relativedelta(fields.Date.today(), rec.birthdate).years

    def _create_new_individual(self):
        self.ensure_one()
        phone = [(0, 0, {"phone_no": self.phone})] if self.phone else None
        individual = (
            self.env["res.partner"]
            .sudo()
            .create(
                {
                    "is_registrant": True,
                    "is_group": False,
                    "name": self.full_name,
                    "given_name": self.given_name,
                    "father_name": self.father_name,
                    "grand_father_name": self.grand_father_name,
                    "family_name": self.family_name,
                    "birth_place": self.birth_place,
                    "birthdate_not_exact": False,
                    "birthdate": self.birthdate,
                    "gender": self.gender,
                    "relation_to_head": self.relation_to_head.id,
                    "phone_number_ids": phone,
                }
            )
        )
        individual.phone_number_ids_change()
        return (
            self.env["g2p.group.membership"]
            .sudo()
            .create(
                {
                    "group": self.parent_id.registrant_id.id,
                    "individual": individual.id,
                    "kind": [(6, 0, self.kind.ids)],
                }
            )
        )
