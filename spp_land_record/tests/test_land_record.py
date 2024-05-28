import json

import pyproj

from odoo.tests.common import TransactionCase


class TestLandRecord(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.res_partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )

        cls.land_record = cls.env["spp.land.record"].create(
            {
                "land_farm_id": cls.res_partner.id,
                "land_name": "Test Land",
                "land_acreage": 10.0,
                "land_use": "cultivation",
                "owner_id": cls.res_partner.id,
                "land_coordinates": json.dumps(
                    {
                        "type": "Point",
                        "coordinates": [124.98706532650226, 7.931953944598931],
                    }
                ),
                "land_geo_polygon": json.dumps(
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [124.935721, 7.956489],
                                [125.008514, 7.941196],
                                [124.999691, 7.890945],
                                [124.935721, 7.956489],
                            ]
                        ],
                    }
                ),
            }
        )

    def test_process_record_to_feature(self):
        proj_from = pyproj.Proj("epsg:4326")
        proj_to = pyproj.Proj("epsg:3857")

        transformer = pyproj.Transformer.from_proj(proj_from, proj_to, always_xy=True).transform
        feature = self.land_record._process_record_to_feature(self.land_record, "polygon", transformer)

        self.assertEqual(feature["type"], "Feature")
        self.assertEqual(feature["properties"]["land_name"], "Test Land")
        self.assertEqual(feature["properties"]["land_use"], "cultivation")
        self.assertEqual(feature["properties"]["land_acreage"], 10.0)
        self.assertEqual(feature["geometry"]["type"], "Polygon")

        feature = self.land_record._process_record_to_feature(self.land_record, "point", transformer)

        self.assertEqual(feature["geometry"]["type"], "Point")
        self.assertEqual(feature["properties"]["land_name"], "Test Land")
        self.assertEqual(feature["properties"]["land_use"], "cultivation")
        self.assertEqual(feature["properties"]["land_acreage"], 10.0)

        feature = self.land_record._process_record_to_feature(self.land_record, "line", transformer)
        self.assertIsNone(feature)

    def test_get_geojson(self):
        geojson = self.env["spp.land.record"].get_geojson(from_srid=4326, to_srid=3857)
        geojson = json.loads(geojson)
        self.assertEqual(geojson["type"], "FeatureCollection")
        self.assertEqual(len(geojson["features"]), 1)
        self.assertEqual(geojson["features"][0]["type"], "Feature")
        self.assertEqual(geojson["features"][0]["properties"]["land_name"], "Test Land")
        self.assertEqual(geojson["features"][0]["properties"]["land_use"], "cultivation")
        self.assertEqual(geojson["features"][0]["properties"]["land_acreage"], 10.0)
        self.assertEqual(geojson["features"][0]["geometry"]["type"], "Polygon")
        self.assertEqual(len(geojson["features"][0]["geometry"]["coordinates"]), 1)
        self.assertEqual(len(geojson["features"][0]["geometry"]["coordinates"][0]), 4)

    def test_get_search_domain_by_geometry_type(self):
        self.assertEqual(self.land_record._get_search_domain_by_geometry_type("point"), [])
