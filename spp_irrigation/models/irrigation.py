from odoo import fields, models


class IrrigationAsset(models.Model):
    _name = "spp.irrigation.asset"
    _description = "Irrigation Asset Details"

    name = fields.Char(string="Irrigation Name/ID")

    category = fields.Selection(
        [
            ("reservoir", "Reservoir"),
        ],
    )

    total_capacity = fields.Float()

    coordinates = fields.GeoPointField()
    geo_polygon = fields.GeoPolygonField()

    irrigation_source_ids = fields.Many2many(
        "spp.irrigation.asset",
        string="Irrigation Sources",
        relation="irrigation_asset_source_rel",
        column1="source_id",
        column2="destination_id",
    )
    irrigation_destination_ids = fields.Many2many(
        "spp.irrigation.asset",
        string="Irrigation Destinations",
        relation="irrigation_asset_destination_rel",
        column1="destination_id",
        column2="source_id",
    )
