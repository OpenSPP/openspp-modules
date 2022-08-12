# Part of Newlogic OpenSPP. See LICENSE file for full copyright and licensing details.
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
    _order = "complete_name"

    parent_id = fields.Many2one("spp.area", "Parent")
    complete_name = fields.Char(
        "Name", compute="_compute_complete_name", recursive=True, store=True
    )
    name = fields.Char("Name", required=True, translate=True)
    parent_path = fields.Char(index=True)
    code = fields.Char("Code")
    altnames = fields.Char("Alternate Name")
    level = fields.Integer("Level")
    child_ids = fields.One2many(
        "spp.area", "id", "Child", compute="_compute_get_childs"
    )

    def _compute_get_childs(self):
        for rec in self:
            child_ids = self.env["spp.area"].search([("parent_id", "=", rec.id)])
            rec.child_ids = child_ids

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for area in self:
            if area.parent_id:
                area.complete_name = "%s > %s" % (
                    area.parent_id.complete_name,
                    area.name,
                )
            else:
                area.complete_name = area.name

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
