from shapely.geometry import Point
from shapely.geometry.collection import GeometryCollection
from shapely.wkt import loads as wktloads

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

from odoo.addons.spp_base_gis.fields import GeoField, GeoLineStringField, GeoPointField, GeoPolygonField, value_to_shape


class FieldsTest(TransactionCase):
    def setUp(self):
        super().setUp()
        self.test_model = self.env["spp.base.gis.test.model"].sudo()
        self.point_field = self.test_model._fields["geo_point"]
        self.line_field = self.test_model._fields["geo_line"]
        self.polygon_field = self.test_model._fields["geo_polygon_field"]

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

    def test_transform_geometry_srid(self):
        from_srid = 4326
        to_srid = 3857

        value = None
        self.assertIsNone(GeoField.transform_geometry_srid(value, from_srid, to_srid))

        value = {"type": "Point", "coordinates": [1, 2]}
        result = GeoField.transform_geometry_srid(value, from_srid, to_srid)
        self.assertNotEqual(result, value)
        self.assertIsInstance(result, str)

        result = GeoField.transform_geometry_srid(value, from_srid, to_srid, output="geom")
        self.assertNotEqual(result.wkt, value)
        self.assertIsInstance(result, Point)

    def test_value_to_shape(self):
        class CustomClass:
            def __init__(self, wkt):
                self.wkt = wkt

        # None Value
        value = None
        result = value_to_shape(value)
        self.assertIsInstance(result, GeometryCollection)
        self.assertTrue(result.is_empty)
        self.assertEqual(result.wkt, "GEOMETRYCOLLECTION EMPTY")
        self.assertEqual(result.geom_type, GeometryCollection.__name__)

        # GeoJson
        value = '{"type": "Point", "coordinates": [1, 2]}'
        result = value_to_shape(value)
        self.assertIsInstance(result, Point)
        self.assertEqual(result.wkt, "POINT (1 2)")
        self.assertEqual(result.geom_type, Point.__name__)
        self.assertEqual(result.x, 1)
        self.assertEqual(result.y, 2)
        self.assertEqual(result.is_empty, False)

        # Hex WKB
        value = "01010000005839B4C876BEF33F83C0CAA145B61640"
        result = value_to_shape(value, use_wkb=True)
        self.assertIsInstance(result, Point)
        self.assertEqual(result.wkt, "POINT (1.234 5.678)")
        self.assertEqual(result.geom_type, Point.__name__)
        self.assertEqual(result.x, 1.234)
        self.assertEqual(result.y, 5.678)
        self.assertEqual(result.is_empty, False)

        # WKT
        value = "Point (1 2)"
        result = value_to_shape(value)
        self.assertIsInstance(result, Point)
        self.assertEqual(result.wkt, "POINT (1 2)")
        self.assertEqual(result.geom_type, Point.__name__)
        self.assertEqual(result.x, 1)
        self.assertEqual(result.y, 2)
        self.assertEqual(result.is_empty, False)

        # BaseGeometry
        value = Point(1, 2)
        result = value_to_shape(value)
        self.assertEqual(result.wkt, "POINT (1 2)")
        self.assertEqual(result.geom_type, Point.__name__)
        self.assertEqual(result.x, 1)
        self.assertEqual(result.y, 2)
        self.assertEqual(result.is_empty, False)

        # CustomClass
        value = CustomClass("Point (1 2)")
        result = value_to_shape(value)
        self.assertEqual(result.wkt, "POINT (1 2)")
        self.assertEqual(result.geom_type, Point.__name__)
        self.assertEqual(result.x, 1)
        self.assertEqual(result.y, 2)
        self.assertEqual(result.is_empty, False)

        # TypeError
        value = ["Invalid Value"]
        with self.assertRaisesRegex(
            TypeError, "Write/create/search geo type must be wkt/geojson string or must respond to wkt"
        ):
            result = value_to_shape(value)

    def test_convert_to_cache(self):
        value = None
        result = self.point_field.convert_to_cache(value, None)
        self.assertIsNone(result)

        value = "10"
        result = self.point_field.convert_to_cache(value, None)
        self.assertEqual(result, value)

        value = "POINT(1 2)"
        result = self.point_field.convert_to_cache(value, None)
        self.assertIsInstance(result, str)
        self.assertEqual(wktloads(value).wkb_hex, result)

    def test_convert_to_record(self):
        value = None
        result = self.point_field.convert_to_record(value, None)
        self.assertFalse(result)

        value = "01010000005839B4C876BEF33F83C0CAA145B61640"
        result = self.point_field.convert_to_record(value, None)
        self.assertIsInstance(result, Point)
        self.assertEqual(result.wkt, "POINT (1.234 5.678)")
        self.assertEqual(result.geom_type, Point.__name__)
        self.assertEqual(result.x, 1.234)
        self.assertEqual(result.y, 5.678)
        self.assertEqual(result.is_empty, False)

    def test_convert_to_read(self):
        value = None
        result = self.point_field.convert_to_read(value, None)
        self.assertFalse(result)

        value = "01010000005839B4C876BEF33F83C0CAA145B61640"
        result = self.point_field.convert_to_read(value, None)
        self.assertIsInstance(result, str)
        self.assertEqual(result, '{"type": "Point", "coordinates": [1.234, 5.678]}')

        value = Point()
        result = self.point_field.convert_to_read(value, None)
        self.assertFalse(result)

        value = Point(1, 2)
        result = self.point_field.convert_to_read(value, None)
        self.assertIsInstance(result, str)
        self.assertEqual(result, '{"type": "Point", "coordinates": [1.0, 2.0]}')

    def test_check_geometry_columns(self):
        cursor = self.test_model._cr
        table_name = self.test_model._table
        column_name = self.point_field.name
        expected_values = (self.point_field.srid, self.point_field.geo_type.upper(), self.point_field.dim)

        expected_values = (3857, self.point_field.geo_type.upper(), 3)
        result = self.point_field.check_geometry_columns(cursor, table_name, column_name, expected_values)
        self.assertFalse(result)

    def test_update_geometry_columns(self):
        cursor = self.test_model._cr
        table_name = self.test_model._table
        column_name = self.point_field.name
        expected_values = (3857, self.point_field.geo_type.upper(), 3)

        with self.assertRaisesRegex(
            ValidationError, f"Geometry column validation failed for table '{table_name}', column '{column_name}'."
        ):
            self.point_field.update_geometry_columns(cursor, table_name, column_name, expected_values)
