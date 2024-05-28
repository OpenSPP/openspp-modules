import json

from odoo.tests.common import TransactionCase


class Common(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_model = cls.env["spp.base.gis.test.model"].sudo()

        cls.geojson_polygon_1 = {
            "type": "Polygon",
            "coordinates": [
                [
                    [124.719702, 7.848172],
                    [124.750567, 7.848008],
                    [124.76422, 7.836532],
                    [124.681638, 7.833007],
                    [124.680976, 7.84891],
                    [124.719702, 7.848172],
                ]
            ],
        }

        cls.test_record_1 = cls.test_model.create(
            {
                "name": "Record 1",
                "geo_polygon_field": json.dumps(cls.geojson_polygon_1),
            }
        )

        cls.geojson_polygon_2 = {
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

        cls.test_record_2 = cls.test_model.create(
            {
                "name": "Record 2",
                "geo_polygon_field": json.dumps(cls.geojson_polygon_2),
            }
        )

        # Coordinates of a point inside Record 1's polygon
        cls.longitude_1, cls.latitude_1 = 124.7291574142456, 7.841423068566499

        # Coordinates of a point inside Record 2's polygon
        cls.longitude_2, cls.latitude_2 = 124.98706532650226, 7.931953944598931

        # Coordinates of a point outside both polygons
        cls.longitude_3, cls.latitude_3 = 124.81488191551932, 7.773921858866217
