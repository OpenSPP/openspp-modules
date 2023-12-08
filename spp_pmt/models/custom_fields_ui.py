# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class OpenSPPCustomFieldsUI(models.Model):
    _inherit = "ir.model.fields"

    field_weight = fields.Float("Default Weight", default=0)
    with_weight = fields.Boolean(default=False)
    area_ids = fields.One2many("spp.fields.area", "field_id", string="Areas")


class OpenSPPCustomFieldsArea(models.Model):
    _name = "spp.fields.area"
    _description = "Fields Area"

    field_id = fields.Many2one("ir.model.fields")
    name = fields.Many2one("spp.area", required=True, string="Area")
    weight = fields.Float(required=True, default=0)
