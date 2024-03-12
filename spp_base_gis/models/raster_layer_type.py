from odoo import fields, models


class OpenSPPGisRasterLayerType(models.Model):
    _name = "spp.gis.raster.layer.type"
    _description = "Raster Layer Type"

    name = fields.Char(translate=True, required=True)
    code = fields.Char(required=True)
    service = fields.Char(required=True)
