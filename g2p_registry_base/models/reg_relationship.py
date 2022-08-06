# Part of Newlogic G2P. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class G2PRegistryRelationship(models.Model):
    _name = "g2p.reg.rel"
    _description = "Registrant Relationship"
    _order = "id desc"
    _inherit = ["mail.thread"]

    registrant1 = fields.Many2one(
        "res.partner",
        "Registrant 1",
        required=True,
        domain=[("is_registrant", "=", True)],
    )
    registrant2 = fields.Many2one(
        "res.partner",
        "Registrant 2",
        required=True,
        domain=[("is_registrant", "=", True)],
    )
    relation = fields.Many2one("g2p.relationship", "Relation")
    disabled = fields.Datetime("Date Disabled")
    disabled_by = fields.Many2one("res.users", "Disabled by")
    start_date = fields.Datetime("Start Date")
    end_date = fields.Datetime("End Date")

    @api.constrains("registrant1", "registrant2")
    def _check_registrants(self):
        for rec in self:
            if rec.registrant1 == rec.registrant2:
                raise ValidationError(
                    _("Registrant 1 and Registrant 2 cannot be the same.")
                )

    @api.constrains("start_date", "end_date")
    def _check_dates(self):
        for record in self:
            if (
                record.start_date
                and record.end_date
                and record.start_date > record.end_date
            ):
                raise ValidationError(
                    _("The starting date cannot be after the ending date.")
                )

    @api.constrains("registrant1", "relation", "registrant2", "start_date", "end_date")
    def _check_relation_uniqueness(self):
        """Forbid multiple active relations of the same type between the same
        partners
        :raises ValidationError: When constraint is violated
        """
        # pylint: disable=no-member
        # pylint: disable=no-value-for-parameter
        for record in self:
            domain = [
                ("relation", "=", record.relation.id),
                ("id", "!=", record.id),
                ("registrant1", "=", record.registrant1.id),
                ("registrant2", "=", record.registrant2.id),
            ]
            if record.start_date:
                domain += [
                    "|",
                    ("end_date", "=", False),
                    ("end_date", ">=", record.start_date),
                ]
            if record.end_date:
                domain += [
                    "|",
                    ("start_date", "=", False),
                    ("start_date", "<=", record.end_date),
                ]
            if record.search(domain):
                raise ValidationError(
                    _("There is already a similar relation with " "overlapping dates")
                )

    @api.constrains("registrant1", "relation")
    def _check_registrant1(self):
        self._check_partner("1")

    @api.constrains("registrant2", "relation")
    def _check_registrant2(self):
        self._check_partner("2")

    def _check_partner(self, side):
        for record in self:
            assert side in ["1", "2"]
            ptype = getattr(record.relation, "registrant_type_%s" % side)
            partner = getattr(record, "registrant%s" % side)
            if (
                not partner.is_registrant
                or (ptype == "i" and partner.is_group)
                or (ptype == "g" and not partner.is_group)
            ):
                raise ValidationError(
                    _("This registrant is not applicable for this " "relation type.")
                )

    def name_get(self):
        res = super(G2PRegistryRelationship, self).name_get()
        for rec in self:
            name = ""
            if rec.registrant1:
                name += rec.registrant1.name
            if rec.registrant2:
                name += " / " + rec.registrant2.name
            res.append((rec.id, name))
        return res

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = args or []
        if name:
            args = [
                "|",
                ("registrant1", operator, name),
                ("registrant2", operator, name),
            ] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)

    def disable_relationship(self):
        for rec in self:
            if not rec.disabled:
                rec.update(
                    {
                        "disabled": fields.Datetime.now(),
                        "disabled_by": self.env.user,
                    }
                )

    def enable_relationship(self):
        for rec in self:
            if rec.disabled:
                rec.update(
                    {
                        "disabled": None,
                        "disabled_by": None,
                    }
                )

    def open_relationship1_form(self):
        if self.registrant1.is_group:
            return {
                "name": "Related Group",
                "view_mode": "form",
                "res_model": "res.partner",
                "res_id": self.registrant1.id,
                "view_id": self.env.ref("g2p_registry_base.view_groups_form").id,
                "type": "ir.actions.act_window",
                "target": "new",
            }
        else:
            return {
                "name": "Related Registrant",
                "view_mode": "form",
                "res_model": "res.partner",
                "res_id": self.registrant1.id,
                "view_id": self.env.ref("g2p_registry_base.view_individuals_form").id,
                "type": "ir.actions.act_window",
                "target": "new",
            }

    def open_relationship2_form(self):
        if self.registrant2.is_group:
            return {
                "name": "Other Related Group",
                "view_mode": "form",
                "res_model": "res.partner",
                "res_id": self.registrant2.id,
                "view_id": self.env.ref("g2p_registry_base.view_groups_form").id,
                "type": "ir.actions.act_window",
                "target": "new",
            }
        else:
            return {
                "name": "Other Related Registrant",
                "view_mode": "form",
                "res_model": "res.partner",
                "res_id": self.registrant2.id,
                "view_id": self.env.ref("g2p_registry_base.view_individuals_form").id,
                "type": "ir.actions.act_window",
                "target": "new",
            }


class G2PRelationship(models.Model):
    _name = "g2p.relationship"
    _description = "Relationship"
    _order = "id desc"

    name = fields.Char("Name", translate=True)
    name_inverse = fields.Char(string="Inverse name", required=True, translate=True)
    bidirectional = fields.Boolean("Bi-directional", default=False)
    registrant_type_1 = fields.Selection(
        selection="get_partner_types", string="Registrant 1 partner type"
    )
    registrant_type_2 = fields.Selection(
        selection="get_partner_types", string="Registrant 2 partner type"
    )

    @api.model
    def get_partner_types(self):
        """A partner can be an organisation or an individual."""
        # pylint: disable=no-self-use
        return [("g", _("Group")), ("i", _("Individual"))]
