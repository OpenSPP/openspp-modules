# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging
import textwrap

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class OpenSPPArea(models.Model):
    _name = "spp.area"
    _description = "Area"
    _order = "id desc"
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = "complete_name"
    _order = "parent_id,name"

    parent_id = fields.Many2one("spp.area", "Parent")
    complete_name = fields.Char(
        "Name", compute="_compute_complete_name", recursive=True, translate=True
    )
    name = fields.Char(required=True, translate=True)
    parent_path = fields.Char(index=True)
    code = fields.Char()
    altnames = fields.Char("Alternate Name")
    level = fields.Integer(help="This is the area level for importing")
    area_level = fields.Integer(
        compute="_compute_area_level", help="This is the main area level"
    )
    child_ids = fields.One2many(
        "spp.area", "id", "Child", compute="_compute_get_childs"
    )
    kind = fields.Many2one("spp.area.kind")

    def _compute_get_childs(self):
        for rec in self:
            child_ids = self.env["spp.area"].search([("parent_id", "=", rec.id)])
            rec.child_ids = child_ids

    @api.depends("parent_id")
    def _compute_area_level(self):
        for rec in self:
            if rec.parent_id:
                rec.area_level = rec.parent_id.area_level + 1
            else:
                rec.area_level = 0

    @api.onchange("parent_id")
    def _onchange_parent_id(self):
        for rec in self:
            if rec.area_level > 10:
                raise ValidationError(
                    _(
                        textwrap.fill(
                            textwrap.dedent(
                                """Max level exceeded! Can't have area with level greater
                        than 10 and your current area is level %s."""
                                % rec.area_level
                            )
                        )
                    )
                )

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for rec in self:
            cur_lang = rec._context.get("lang", False)
            area_name = rec.env["ir.translation"]._get_ids(
                "spp.area,name", "model", cur_lang, rec.ids
            )

            if rec.id:
                if rec.parent_id:
                    if area_name[rec.id]:
                        rec.complete_name = "%s > %s" % (
                            rec.parent_id.complete_name,
                            area_name[rec.id],
                        )
                    else:
                        rec.complete_name = "%s > %s" % (
                            rec.parent_id.complete_name,
                            rec.name,
                        )
                else:
                    rec.complete_name = rec.name
                    if area_name[rec.id]:
                        rec.complete_name = area_name[rec.id]

            else:
                rec.complete_name = None

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = args or []
        domain = []
        if name:
            domain = [("name", operator, name)]

        return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)

    @api.model
    def create(self, vals):
        area_name = self.name
        if "name" in vals:
            area_name = vals["name"]
        area_code = self.code
        if "code" in vals:
            area_code = vals["code"]
        curr_area = self.env["spp.area"].search(
            [
                ("name", "=", area_name),
                ("code", "=", area_code),
            ]
        )

        if curr_area:
            raise ValidationError(_("Area already exist!"))
        else:
            Area = super(OpenSPPArea, self).create(vals)
            Languages = self.env["res.lang"].search([("active", "=", True)])
            vals_list = []
            for lang_code in Languages:
                vals_list.append(
                    {
                        "name": "spp.area,name",
                        "lang": lang_code.code,
                        "res_id": Area.id,
                        "src": Area.name,
                        "value": None,
                        "state": "to_translate",
                        "type": "model",
                    }
                )

            self.env["ir.translation"]._upsert_translations(vals_list)
            return Area

    def write(self, vals):
        for rec in self:
            area_name = rec.name
            if "name" in vals:
                area_name = vals["name"]
            area_code = rec.code
            if "code" in vals:
                area_code = vals["code"]
            curr_area = self.env["spp.area"].search(
                [
                    ("name", "=", area_name),
                    ("code", "=", area_code),
                    ("id", "!=", rec.id),
                ]
            )
            if curr_area:
                raise ValidationError(_("Area already exist!"))
            else:
                return super(OpenSPPArea, self).write(vals)


class OpenSPPAreaKind(models.Model):
    _name = "spp.area.kind"
    _description = "Area Kind"
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = "complete_name"
    _order = "parent_id,name"

    parent_id = fields.Many2one("spp.area.kind", "Parent")
    parent_path = fields.Char(index=True)
    name = fields.Char(required=True)
    complete_name = fields.Char(
        "Name", compute="_compute_complete_name", recursive=True, translate=True
    )

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for rec in self:
            if rec.id:
                if rec.parent_id:
                    rec.complete_name = "%s > %s" % (
                        rec.parent_id.complete_name,
                        rec.name,
                    )
                else:
                    rec.complete_name = rec.name
            else:
                rec.complete_name = None

    def unlink(self):
        for rec in self:
            external_identifier = self.env["ir.model.data"].search(
                [("res_id", "=", rec.id), ("model", "=", "spp.area.kind")]
            )
            if external_identifier and external_identifier.name:
                raise ValidationError(_("Can't delete default Area Kind"))
            else:
                areas = self.env["spp.area"].search([("kind", "=", rec.id)])
                if areas:
                    raise ValidationError(_("Can't delete used Area Kind"))
                else:
                    return super(OpenSPPAreaKind, self).unlink()

    def write(self, vals):
        for rec in self:
            external_identifier = self.env["ir.model.data"].search(
                [("res_id", "=", rec.id), ("model", "=", "spp.area.kind")]
            )
            if external_identifier and external_identifier.name:
                raise ValidationError(_("Can't edit default Area Kind"))
            else:
                return super(OpenSPPAreaKind, self).write(vals)
