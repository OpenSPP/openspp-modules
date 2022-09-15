# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, fields, models

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
    level = fields.Integer()
    child_ids = fields.One2many(
        "spp.area", "id", "Child", compute="_compute_get_childs"
    )

    def _compute_get_childs(self):
        for rec in self:
            child_ids = self.env["spp.area"].search([("parent_id", "=", rec.id)])
            rec.child_ids = child_ids

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        cur_lang = self._context.get("lang", False)
        area_name = self.env["ir.translation"]._get_ids(
            "spp.area,name", "model", cur_lang, self.ids
        )
        for area in self:
            if area.id:
                if area.parent_id:
                    area.complete_name = "%s > %s" % (
                        area.parent_id.complete_name,
                        area_name[area.id],
                    )
                else:
                    area.complete_name = area_name[area.id]
            else:
                area.complete_name = None

    @api.model
    def create(self, vals):
        Area = super(OpenSPPArea, self).create(vals)
        _logger.info("Area ID: %s" % Area.id)
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
