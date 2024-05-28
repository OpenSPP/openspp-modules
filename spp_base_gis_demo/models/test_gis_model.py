from odoo import fields, models


class GisTestModel(models.Model):
    _name = "spp.base.gis.test.model"
    _description = "GIS Test Model"

    name = fields.Char()
    geo_polygon_field = fields.GeoPolygonField()
    geo_line = fields.GeoLineStringField()
    geo_point = fields.GeoPointField()
