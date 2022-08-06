# Part of Newlogic G2P. See LICENSE file for full copyright and licensing details.

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class G2PGroupMembership(models.Model):
    _name = "g2p.group.membership"
    _description = "Group Membership"
    _order = "id desc"
    _inherit = ["mail.thread"]

    group = fields.Many2one(
        "res.partner",
        "Group",
        required=True,
        domain=[("is_group", "=", True), ("is_registrant", "=", True)],
    )
    individual = fields.Many2one(
        "res.partner",
        "Individual",
        required=True,
        domain=[("is_group", "=", False), ("is_registrant", "=", True)],
    )
    kind = fields.Many2many("g2p.group.membership.kind", string="Kind")
    start_date = fields.Datetime(
        "Start Date", default=lambda self: fields.Datetime.now()
    )
    end_date = fields.Datetime(
        "End Date"
    )  # TODO: Should rename `ended_date` add a check that the date is in the past

    @api.onchange("kind")
    def _kind_onchange(self):
        origin_length = len(self._origin.kind.ids)
        new_length = len(self.kind.ids)
        if new_length > origin_length:
            unique_kinds = self.env["g2p.group.membership.kind"].search(
                [("is_unique", "=", True)]
            )
            for unique_kind_id in unique_kinds:
                unique_count = 0
                for line in self.group.group_membership_ids:

                    for rec_line in line.kind:

                        kind_id = str(rec_line.id)
                        kind_str = ""
                        for m in kind_id:
                            if m.isdigit():
                                kind_str = kind_str + m
                        if rec_line.id == unique_kind_id.id or kind_str == str(
                            unique_kind_id.id
                        ):
                            unique_count += 1
                if unique_count > 1:
                    raise ValidationError(
                        _("Only one %s is allowed per group" % unique_kind_id.name)
                    )

    @api.constrains("individual")
    def _check_group_members(self):
        for rec in self:
            rec_count = 0
            for group_membership_id in rec.group.group_membership_ids:
                if rec.individual.id == group_membership_id.individual.id:
                    rec_count += 1
            if rec_count > 1:
                raise ValidationError(_("Duplication of Member is not allowed "))

    def name_get(self):
        res = super(G2PGroupMembership, self).name_get()
        for rec in self:
            name = "NONE"
            if rec.group:
                name = rec.group.name
            res.append((rec.id, name))
        return res

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = args or []
        if name:
            args = [("group", operator, name)] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)

    def _recompute_parent_groups(self, records):
        fields = self._get_calculated_group_fields()
        for line in records:
            for field in fields:
                self.env.add_to_compute(field, line.group)

    def _get_calculated_group_fields(self):
        model_fields_id = self.env["res.partner"]._fields
        fields = []
        for field_name, field in model_fields_id.items():
            els = field_name.split("_")
            if field.compute and len(els) >= 3 and els[2] == "grp" and els[1] == "crt":
                fields.append(field)
        return fields

    def write(self, vals):
        res = super(G2PGroupMembership, self).write(vals)
        self._recompute_parent_groups(self)
        return res

    @api.model_create_multi
    @api.returns("self", lambda value: value.id)
    def create(self, vals_list):
        res = super(G2PGroupMembership, self).create(vals_list)
        self._recompute_parent_groups(res)
        return res

    def unlink(self):
        groups = self.mapped("group")
        res = super(G2PGroupMembership, self).unlink()
        fields = self._get_calculated_group_fields()
        for group in groups:
            for field in fields:
                self.env.add_to_compute(field, group)
        return res

    def open_individual_form(self):
        return {
            "name": "Individual Member",
            "view_mode": "form",
            "res_model": "res.partner",
            "res_id": self.individual.id,
            "view_id": self.env.ref("g2p_registry_individual.view_individuals_form").id,
            "type": "ir.actions.act_window",
            "target": "new",
            "context": {"default_is_group": False},
            "flags": {"mode": "readonly"},
        }

    def open_group_form(self):
        return {
            "name": "Group Membership",
            "view_mode": "form",
            "res_model": "res.partner",
            "res_id": self.group.id,
            "view_id": self.env.ref("g2p_registry_group.view_groups_form").id,
            "type": "ir.actions.act_window",
            "target": "new",
            "context": {"default_is_group": True},
            "flags": {"mode": "readonly"},
        }


class G2PGroupMembershipKind(models.Model):
    _name = "g2p.group.membership.kind"
    _description = "Group Membership Kind"
    _order = "id desc"

    name = fields.Char("Kind")
    is_unique = fields.Boolean("Unique")

    def unlink(self):
        for rec in self:
            external_identifier = self.env["ir.model.data"].search(
                [("res_id", "=", rec.id), ("model", "=", "g2p.group.membership.kind")]
            )
            if external_identifier.name in (
                "group_membership_kind_head",
                "group_membership_kind_principal",
                "group_membership_kind_alternative",
            ):
                raise ValidationError(_("Can't delete default kinds"))
            else:
                return super(G2PGroupMembershipKind, self).unlink()

    def write(self, vals):
        external_identifier = self.env["ir.model.data"].search(
            [("res_id", "=", self.id), ("model", "=", "g2p.group.membership.kind")]
        )
        if external_identifier.name in (
            "group_membership_kind_head",
            "group_membership_kind_principal",
            "group_membership_kind_alternative",
        ):
            raise ValidationError(_("Can't edit default kinds"))
        else:
            return super(G2PGroupMembershipKind, self).write(vals)
