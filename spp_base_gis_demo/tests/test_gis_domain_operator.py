import json

from shapely.geometry import Point

from .common import Common


class GisDomainOperatorTest(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # geojson of a point inside geojson_polygon_1
        cls.geojson_point_1 = {
            "type": "Point",
            "coordinates": [cls.longitude_1, cls.latitude_1],
        }

        # geojson of a point inside geojson_polygon_2
        cls.geojson_point_2 = {
            "type": "Point",
            "coordinates": [cls.longitude_2, cls.latitude_2],
        }

        # geojson of a point outside both geojson_polygon_1 and geojson_polygon_2
        cls.geojson_point_3 = {
            "type": "Point",
            "coordinates": [cls.longitude_3, cls.latitude_3],
        }

    def test_gis_intersects(self):
        domain = [("geo_polygon_field", "gis_intersects", self.geojson_point_1)]
        record_1 = self.test_model.search(domain, limit=1)

        domain = [("geo_polygon_field", "gis_intersects", self.geojson_point_2)]
        record_2 = self.test_model.search(domain, limit=1)

        domain = [("geo_polygon_field", "gis_intersects", self.geojson_point_3)]
        record_3 = self.test_model.search(domain, limit=1)

        self.assertEqual(record_1, self.test_record_1)
        self.assertEqual(record_2, self.test_record_2)
        self.assertFalse(record_3)

    def test_gis_intersects_with_distance(self):
        domain = [("geo_polygon_field", "gis_intersects", (self.geojson_point_1, 1000))]
        record_1 = self.test_model.search(domain, limit=1)

        domain = [("geo_polygon_field", "gis_intersects", (self.geojson_point_2, 1000))]
        record_2 = self.test_model.search(domain, limit=1)

        domain = [("geo_polygon_field", "gis_intersects", (self.geojson_point_3, 1000))]
        record_3 = self.test_model.search(domain, limit=1)

        self.assertEqual(record_1, self.test_record_1)
        self.assertEqual(record_2, self.test_record_2)
        self.assertFalse(record_3)

    def test_gis_within(self):
        domain = [("geo_polygon_field", "gis_within", self.geojson_point_1)]
        record_1 = self.test_model.search(domain, limit=1)

        domain = [("geo_polygon_field", "gis_within", self.geojson_point_2)]
        record_2 = self.test_model.search(domain, limit=1)

        domain = [("geo_polygon_field", "gis_within", self.geojson_point_3)]
        record_3 = self.test_model.search(domain, limit=1)

        self.assertEqual(record_1, self.test_record_1)
        self.assertEqual(record_2, self.test_record_2)
        self.assertFalse(record_3)

    def test_gis_within_with_distance(self):
        domain = [("geo_polygon_field", "gis_within", (self.geojson_point_1, 1000))]
        record_1 = self.test_model.search(domain, limit=1)

        domain = [("geo_polygon_field", "gis_within", (self.geojson_point_2, 1000))]
        record_2 = self.test_model.search(domain, limit=1)

        domain = [("geo_polygon_field", "gis_within", (self.geojson_point_3, 1000))]
        record_3 = self.test_model.search(domain, limit=1)

        self.assertFalse(record_1)
        self.assertEqual(record_2, self.test_record_2)
        self.assertFalse(record_3)

    def test_gis_contains(self):
        domain = [("geo_polygon_field", "gis_contains", self.geojson_point_1)]
        record_1 = self.test_model.search(domain, limit=1)

        domain = [("geo_polygon_field", "gis_contains", self.geojson_point_2)]
        record_2 = self.test_model.search(domain, limit=1)

        domain = [("geo_polygon_field", "gis_contains", self.geojson_point_3)]
        record_3 = self.test_model.search(domain, limit=1)

        self.assertFalse(record_1)
        self.assertFalse(record_2)
        self.assertFalse(record_3)

    def test_gis_contains_with_distance(self):
        domain = [("geo_polygon_field", "gis_contains", (self.geojson_point_1, 10000))]
        record_1 = self.test_model.search(domain, limit=1)

        domain = [("geo_polygon_field", "gis_contains", (self.geojson_point_2, 10000))]
        record_2 = self.test_model.search(domain, limit=1)

        domain = [("geo_polygon_field", "gis_contains", (self.geojson_point_3, 1000))]
        record_3 = self.test_model.search(domain, limit=1)

        self.assertEqual(record_1, self.test_record_1)
        self.assertEqual(record_2, self.test_record_2)
        self.assertFalse(record_3)

    def test_gis_covers(self):
        domain = [("geo_polygon_field", "gis_covers", self.geojson_point_1)]
        record_1 = self.test_model.search(domain, limit=1)

        domain = [("geo_polygon_field", "gis_covers", self.geojson_point_2)]
        record_2 = self.test_model.search(domain, limit=1)

        domain = [("geo_polygon_field", "gis_covers", self.geojson_point_3)]
        record_3 = self.test_model.search(domain, limit=1)

        self.assertFalse(record_1)
        self.assertFalse(record_2)
        self.assertFalse(record_3)

    def test_gis_covers_with_distance(self):
        domain = [("geo_polygon_field", "gis_covers", (self.geojson_point_1, 10000))]
        record_1 = self.test_model.search(domain, limit=1)

        domain = [("geo_polygon_field", "gis_covers", (self.geojson_point_2, 10000))]
        record_2 = self.test_model.search(domain, limit=1)

        domain = [("geo_polygon_field", "gis_covers", (self.geojson_point_3, 1000))]
        record_3 = self.test_model.search(domain, limit=1)

        self.assertEqual(record_1, self.test_record_1)
        self.assertEqual(record_2, self.test_record_2)
        self.assertFalse(record_3)

    def test_gis_equals(self):
        domain = [("geo_polygon_field", "gis_equals", self.geojson_point_1)]
        record_1 = self.test_model.search(domain, limit=1)

        domain = [("geo_polygon_field", "gis_equals", self.geojson_point_2)]
        record_2 = self.test_model.search(domain, limit=1)

        domain = [("geo_polygon_field", "gis_equals", self.geojson_point_3)]
        record_3 = self.test_model.search(domain, limit=1)

        self.assertFalse(record_1)
        self.assertFalse(record_2)
        self.assertFalse(record_3)

    def test_gis_equals_with_distance(self):
        domain = [("geo_polygon_field", "gis_equals", (self.geojson_point_1, 10000))]
        record_1 = self.test_model.search(domain, limit=1)

        domain = [("geo_polygon_field", "gis_equals", (self.geojson_point_2, 10000))]
        record_2 = self.test_model.search(domain, limit=1)

        domain = [("geo_polygon_field", "gis_equals", (self.geojson_point_3, 1000))]
        record_3 = self.test_model.search(domain, limit=1)

        self.assertFalse(record_1)
        self.assertFalse(record_2)
        self.assertFalse(record_3)

    def test_gis_coveredby(self):
        domain = [("geo_polygon_field", "gis_coveredby", self.geojson_point_1)]
        record_1 = self.test_model.search(domain, limit=1)

        domain = [("geo_polygon_field", "gis_coveredby", self.geojson_point_2)]
        record_2 = self.test_model.search(domain, limit=1)

        domain = [("geo_polygon_field", "gis_coveredby", self.geojson_point_3)]
        record_3 = self.test_model.search(domain, limit=1)

        self.assertEqual(record_1, self.test_record_1)
        self.assertEqual(record_2, self.test_record_2)
        self.assertFalse(record_3)

    def test_gis_coveredby_with_distance(self):
        domain = [("geo_polygon_field", "gis_coveredby", (self.geojson_point_1, 1000))]
        record_1 = self.test_model.search(domain, limit=1)

        domain = [("geo_polygon_field", "gis_coveredby", (self.geojson_point_2, 1000))]
        record_2 = self.test_model.search(domain, limit=1)

        domain = [("geo_polygon_field", "gis_coveredby", (self.geojson_point_3, 1000))]
        record_3 = self.test_model.search(domain, limit=1)

        self.assertFalse(record_1)
        self.assertEqual(record_2, self.test_record_2)
        self.assertFalse(record_3)

    def test_gis_disjoint(self):
        domain = [("geo_polygon_field", "gis_disjoint", self.geojson_point_1)]
        record_1 = self.test_model.search(domain)

        domain = [("geo_polygon_field", "gis_disjoint", self.geojson_point_2)]
        record_2 = self.test_model.search(domain)

        domain = [("geo_polygon_field", "gis_disjoint", self.geojson_point_3)]
        record_3 = self.test_model.search(domain)

        self.assertEqual(record_1, self.test_record_2)
        self.assertEqual(record_2, self.test_record_1)
        self.assertEqual(record_3, self.test_record_1 + self.test_record_2)

    def test_gis_disjoint_with_distance(self):
        domain = [("geo_polygon_field", "gis_disjoint", (self.geojson_point_1, 1000))]
        record_1 = self.test_model.search(domain)

        domain = [("geo_polygon_field", "gis_disjoint", (self.geojson_point_2, 1000))]
        record_2 = self.test_model.search(domain)

        domain = [("geo_polygon_field", "gis_disjoint", (self.geojson_point_3, 1000))]
        record_3 = self.test_model.search(domain)

        self.assertEqual(record_1, self.test_record_2)
        self.assertEqual(record_2, self.test_record_1)
        self.assertEqual(record_3, self.test_record_1 + self.test_record_2)

    def test_gis_crosses(self):
        domain = [("geo_polygon_field", "gis_crosses", self.geojson_point_1)]
        record_1 = self.test_model.search(domain)

        domain = [("geo_polygon_field", "gis_crosses", self.geojson_point_2)]
        record_2 = self.test_model.search(domain)

        domain = [("geo_polygon_field", "gis_crosses", self.geojson_point_3)]
        record_3 = self.test_model.search(domain)

        self.assertFalse(record_1)
        self.assertFalse(record_2)
        self.assertFalse(record_3)

    def test_gis_crosses_with_distance(self):
        domain = [("geo_polygon_field", "gis_crosses", (self.geojson_point_1, 100000))]
        record_1 = self.test_model.search(domain)

        domain = [("geo_polygon_field", "gis_crosses", (self.geojson_point_2, 100000))]
        record_2 = self.test_model.search(domain)

        domain = [("geo_polygon_field", "gis_crosses", (self.geojson_point_3, 100000))]
        record_3 = self.test_model.search(domain)

        self.assertFalse(record_1)
        self.assertFalse(record_2)
        self.assertFalse(record_3)

    def test_gis_touches(self):
        domain = [("geo_polygon_field", "gis_touches", self.geojson_point_1)]
        record_1 = self.test_model.search(domain)

        domain = [("geo_polygon_field", "gis_touches", self.geojson_point_2)]
        record_2 = self.test_model.search(domain)

        domain = [("geo_polygon_field", "gis_touches", self.geojson_point_3)]
        record_3 = self.test_model.search(domain)

        self.assertFalse(record_1)
        self.assertFalse(record_2)
        self.assertFalse(record_3)

    def test_gis_touches_with_distance(self):
        domain = [("geo_polygon_field", "gis_touches", (self.geojson_point_1, 1000))]
        record_1 = self.test_model.search(domain)

        domain = [("geo_polygon_field", "gis_touches", (self.geojson_point_2, 1000))]
        record_2 = self.test_model.search(domain)

        domain = [("geo_polygon_field", "gis_touches", (self.geojson_point_3, 1000))]
        record_3 = self.test_model.search(domain)

        self.assertFalse(record_1)
        self.assertFalse(record_2)
        self.assertFalse(record_3)

    def test_gis_domain_error(self):
        domain = [("geo_polygon_field", "invalid", self.geojson_point_1)]

        with self.assertRaises(ValueError):
            self.test_model.search(domain)

    def test_gis_domain_json(self):
        domain = [("geo_polygon_field", "gis_intersects", json.dumps(self.geojson_point_1))]
        record_1 = self.test_model.search(domain, limit=1)

        domain = [("geo_polygon_field", "gis_intersects", json.dumps(self.geojson_point_2))]
        record_2 = self.test_model.search(domain, limit=1)

        domain = [("geo_polygon_field", "gis_intersects", json.dumps(self.geojson_point_3))]
        record_3 = self.test_model.search(domain, limit=1)

        self.assertEqual(record_1, self.test_record_1)
        self.assertEqual(record_2, self.test_record_2)
        self.assertFalse(record_3)

    def test_gis_domain_wkt(self):
        domain = [("geo_polygon_field", "gis_intersects", "POINT(124.7291574142456 7.841423068566499)")]
        record_1 = self.test_model.search(domain, limit=1)

        domain = [("geo_polygon_field", "gis_intersects", "POINT(124.98706532650226 7.931953944598931)")]
        record_2 = self.test_model.search(domain, limit=1)

        domain = [("geo_polygon_field", "gis_intersects", "POINT(124.81488191551932 7.773921858866217)")]
        record_3 = self.test_model.search(domain, limit=1)

        self.assertEqual(record_1, self.test_record_1)
        self.assertEqual(record_2, self.test_record_2)
        self.assertFalse(record_3)

    def test_gis_domain_shape(self):
        domain = [("geo_polygon_field", "gis_intersects", Point(self.longitude_1, self.latitude_1))]
        record_1 = self.test_model.search(domain, limit=1)

        domain = [("geo_polygon_field", "gis_intersects", Point(self.longitude_2, self.latitude_2))]
        record_2 = self.test_model.search(domain, limit=1)

        domain = [("geo_polygon_field", "gis_intersects", Point(self.longitude_3, self.latitude_3))]
        record_3 = self.test_model.search(domain, limit=1)

        self.assertEqual(record_1, self.test_record_1)
        self.assertEqual(record_2, self.test_record_2)
        self.assertFalse(record_3)

    def test_normal_query(self):
        # Just to check if normal query is still working as expected
        domain = [("name", "=", "Record 1")]
        record_1 = self.test_model.search(domain, limit=1)

        domain = [("name", "=", "Record 2")]
        record_2 = self.test_model.search(domain, limit=1)

        self.assertEqual(record_1, self.test_record_1)
        self.assertEqual(record_2, self.test_record_2)
