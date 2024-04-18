from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

from ..fields import GeoLineStringField, GeoPointField, GeoPolygonField


class FieldsTest(TransactionCase):
    def setUp(self):
        super().setUp()
        self.point_field = self.env["spp.base.gis.test.model"]._fields["geo_point"]
        self.line_field = self.env["spp.base.gis.test.model"]._fields["geo_line"]
        self.polygon_field = self.env["spp.base.gis.test.model"]._fields["geo_polygon_field"]

    def test_field_differences(self):
        self.assertEqual(self.point_field.type, "geo_point")
        self.assertEqual(self.point_field.geo_type, "Point")
        self.assertIsInstance(self.point_field, GeoPointField)
        self.assertEqual(self.point_field.geo_class.__name__, "Point")
        self.assertEqual(self.point_field.srid, 4326)
        self.assertEqual(self.point_field.dim, 2)
        self.assertEqual(self.point_field.column_type, ("geometry", "geometry"))

        self.assertEqual(self.line_field.type, "geo_line")
        self.assertEqual(self.line_field.geo_type, "LineString")
        self.assertIsInstance(self.line_field, GeoLineStringField)
        self.assertEqual(self.line_field.geo_class.__name__, "LineString")

        self.assertEqual(self.polygon_field.type, "geo_polygon")
        self.assertEqual(self.polygon_field.geo_type, "Polygon")
        self.assertIsInstance(self.polygon_field, GeoPolygonField)
        self.assertEqual(self.polygon_field.geo_class.__name__, "Polygon")

    def test_validate_value(self):
        value = "POINT(1 2)"
        with self.assertRaises(ValidationError):
            self.point_field.validate_value(value)

        value = "[{}]"
        with self.assertRaisesRegex(ValidationError, "Value should be a geojson"):
            self.point_field.validate_value(value)

        value = '{"type": "Point"}'
        with self.assertRaisesRegex(ValidationError, "type and coordinates should be in the geojson"):
            self.point_field.validate_value(value)

        value = '{"type": "Circle", "coordinates": [1, 2]}'
        with self.assertRaisesRegex(ValidationError, "Circle is not a valid type."):
            self.point_field.validate_value(value)

        value = '{"type": "Point", "coordinates": []}'
        with self.assertRaisesRegex(ValidationError, "Geometry is empty."):
            self.point_field.validate_value(value)
