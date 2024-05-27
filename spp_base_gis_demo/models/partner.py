from odoo import fields, models


class ResPartner(models.Model):
    """Add geo_point to partner using a function filed"""

    _inherit = "res.partner"

    geo_point = fields.GeoPointField(string="Geo Point")
    geo_line = fields.GeoLineStringField(string="Geo Line")
    geo_polygon_field = fields.GeoPolygonField(string="Geo Polygon")
