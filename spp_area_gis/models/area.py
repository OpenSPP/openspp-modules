from odoo import fields, models


class OpenSPPArea(models.Model):
    _inherit = "spp.area"

    coordinates = fields.GeoPointField(string="Coordinates")
    geo_polygon = fields.GeoPolygonField(string="Area Polygon")
