import json

import pyproj
from shapely.geometry import mapping
from shapely.ops import transform

from odoo import api, fields, models


# TODO: Move it to its own module Independent of farm_base
class LandRecord(models.Model):
    _name = "spp.land.record"
    _description = "Land Record Details"
    _record_name = "land_name"

    land_farm_id = fields.Many2one("res.partner", string="Farm")
    land_name = fields.Char(string="Parcel Name/ID")
    land_acreage = fields.Float()

    # TODO: Change to geo_point and geo_polygon
    land_coordinates = fields.GeoPoint()
    land_geo_polygon = fields.GeoMultiPolygon()

    land_use = fields.Selection(
        [
            ("cultivation", "Cultivation"),
            ("livestock", "Livestock"),
            ("aquaculture", "Aquaculture"),
            ("mixed", "Mixed Use"),
            ("fallow", "Fallow"),
            ("leased_out", "Leased Out"),
            ("other", "Other"),
        ],
    )

    # list of `spp.species`` for livestock and aquaculture
    # when land_use is mixed, do not restrict the species
    species = fields.Many2many(
        "spp.farm.species"
        # domain="['|',('species_type', '=', land_use),(land_use, '=', 'mixed')]",
    )
    species_domain = fields.Binary(compute="_compute_species_domain")

    cultivation_method = fields.Selection(
        [("irrigated", "Irrigated"), ("rainfed", "Rainfed")],
        help="Relevant if land use is cultivation or mixed",
    )

    @api.depends("land_use")
    def _compute_species_domain(self):
        for rec in self:
            species_domain = []
            if rec.land_use != "mixed":
                species_domain = [("species_type", "=", rec.land_use)]

            rec.species_domain = species_domain

    def _process_record_to_feature(self, record, geometry_type, transformer):
        """
        Convert a record to a GeoJSON feature using shapely and geojson libraries.

        Args:
            record: The record to process.
            geometry_type: The type of geometry to process ('point', 'polygon', or 'all').
            transformer: The transformer to use for the projection.

        Returns:
            A GeoJSON feature dictionary or None if no valid geometry found.
        """
        # Initialize the feature dictionary with properties
        feature = {
            "type": "Feature",
            "properties": {
                "land_name": record.land_name,
                "land_use": record.land_use,
                "land_acreage": record.land_acreage,
                # Include other properties as needed
            },
        }

        # Process polygon geometry with priority
        if geometry_type in ["polygon", "all"] and record.land_geo_polygon:
            # Assuming land_geo_polygon is a shapely object
            feature["geometry"] = mapping(transform(transformer, record.land_geo_polygon))
        # Fallback to point geometry if requested or no polygon is available
        elif geometry_type in ["point", "all"] and record.land_coordinates:
            feature["geometry"] = mapping(transform(transformer, record.coordinates))

        else:
            # No valid geometry found based on the preferences
            return None

        return feature

    @api.model
    def get_geojson(self, geometry_type="all"):
        """
        Generate a GeoJSON representation of land records.

        :param geometry_type: A string specifying the type of geometry to include ('point', 'polygon', or 'all').
        :return: A GeoJSON string of land records.
        """
        search_domain = self._get_search_domain_by_geometry_type(geometry_type)
        land_records = self.search(search_domain)

        # Construct GeoJSON structure
        geojson = {"type": "FeatureCollection", "features": []}

        # Assuming coordinates are in EPSG:3857 (Pseudo-Mercator)
        proj_from = pyproj.Proj("epsg:3857")  # EPSG:3857 - WGS 84 / Pseudo-Mercator
        proj_to = pyproj.Proj("epsg:4326")  # WGS84
        transformer = pyproj.Transformer.from_proj(proj_from, proj_to, always_xy=True).transform

        for record in land_records:
            feature = self._process_record_to_feature(record, geometry_type, transformer)
            if feature:
                geojson["features"].append(feature)

        return json.dumps(geojson, indent=2)

    def _get_search_domain_by_geometry_type(self, geometry_type):
        """
        Determine the search domain based on the requested geometry type.

        :param geometry_type: The geometry type ('point', 'polygon', or 'all').
        :return: A search domain for the ORM.
        """
        # if geometry_type == 'point':
        #     return [('land_coordinates', '!=', False)]
        # elif geometry_type == 'polygon':
        #     return [('land_geo_polygon', '!=', False)]
        # else:  # 'all'
        #     return ['|', ('land_coordinates', '!=', False), ('land_geo_polygon', '!=', False)]
        return []
