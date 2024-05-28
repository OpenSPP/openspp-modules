from odoo import fields, models

from odoo.addons import base

if "gis" not in base.models.ir_actions.VIEW_TYPES:
    base.models.ir_actions.VIEW_TYPES.append(("gis", "GIS"))

GEO_TYPES = [
    ("geo_polygon", "geo_polygon"),
    ("geo_point", "geo_point"),
    ("geo_line", "geo_line"),
]

GEO_TYPES_ONDELETE = {
    "geo_polygon": "cascade",
    "geo_point": "cascade",
    "geo_line": "cascade",
}

POSTGIS_GEO_TYPES = [
    ("POINT", "POINT"),
    ("LINESTRING", "LINESTRING"),
    ("POLYGON", "POLYGON"),
]


class IrModelField(models.Model):
    _inherit = "ir.model.fields"

    srid = fields.Integer("srid", required=False)
    geo_type = fields.Selection(POSTGIS_GEO_TYPES, string="PostGIS type")
    dim = fields.Selection([("2", "2"), ("3", "3"), ("4", "4")], string="PostGIS Dimension", default="2")
    gist_index = fields.Boolean("Create gist index")
    ttype = fields.Selection(
        selection_add=GEO_TYPES,
        ondelete=GEO_TYPES_ONDELETE,
    )
