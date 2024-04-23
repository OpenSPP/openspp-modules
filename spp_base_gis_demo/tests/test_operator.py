from odoo.tests.common import TransactionCase

from odoo.addons.spp_base_gis.operators import Operator


class OperatorTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.gis_field_name = "geo_polygon_field"
        cls.gis_field = cls.env["spp.base.gis.test.model"].sudo()._fields[cls.gis_field_name]
        cls.srid = cls.gis_field.srid
        cls.operator = Operator(cls.gis_field)

    def test_create_point(self):
        longitude, latitude = 1, 2
        point = self.operator.create_point([[longitude, latitude]], self.srid)

        self.assertEqual(point, f"ST_SetSRID(ST_MakePoint({longitude}, {latitude}), {self.srid})")

    def test_create_line(self):
        line = [[1, 2], [3, 4]]
        line_string = self.operator.create_line(line, self.srid)

        self.assertEqual(
            line_string, f"ST_SetSRID(ST_MakeLine(ARRAY[ST_MakePoint(1, 2), ST_MakePoint(3, 4)]), {self.srid})"
        )

    def test_create_polygon(self):
        polygon = [[1, 2], [3, 4], [5, 6], [1, 2]]
        polygon_string = self.operator.create_polygon(polygon, self.srid)

        expected_string = (
            f"ST_SetSRID(ST_MakePolygon(ST_MakeLine(ARRAY[ST_MakePoint(1, 2), "
            f"ST_MakePoint(3, 4), ST_MakePoint(5, 6), ST_MakePoint(1, 2)])), {self.srid})"
        )

        self.assertEqual(polygon_string, expected_string)

    def test_st_transform(self):
        point = "POINT(1 2)"
        srid = 3856
        transformed_point = self.operator.st_transform(point, srid)

        self.assertEqual(transformed_point, f"ST_Transform({point}, {srid})")

    def test_get_postgis_query_point(self):
        operation = "touches"
        longitude, latitude = 1, 2
        query = self.operator.get_postgis_query(operation, [[longitude, latitude]])

        self.assertEqual(
            query, f"ST_Touches(ST_SetSRID(ST_MakePoint({longitude}, {latitude}), {self.srid}), {self.gis_field_name})"
        )

    def test_get_postgis_query_line(self):
        operation = "intersects"
        line = [[1, 2], [3, 4]]
        query = self.operator.get_postgis_query(operation, line, layer_type="line")

        expected_query = (
            f"ST_Intersects("
            f"ST_SetSRID("
            f"ST_MakeLine(ARRAY["
            f"ST_MakePoint(1, 2), "
            f"ST_MakePoint(3, 4)"
            f"]), {self.srid}), {self.gis_field_name})"
        )

        self.assertEqual(query, expected_query)

    def test_get_postgis_query_polygon(self):
        operation = "contains"
        polygon = [[1, 2], [3, 4], [5, 6]]
        query = self.operator.get_postgis_query(operation, polygon, layer_type="polygon")

        expected_query = (
            f"ST_Contains("
            f"ST_SetSRID("
            f"ST_MakePolygon(ST_MakeLine(ARRAY["
            f"ST_MakePoint(1, 2), "
            f"ST_MakePoint(3, 4), "
            f"ST_MakePoint(5, 6), "
            f"ST_MakePoint(1, 2)"
            f"])), {self.srid}), {self.gis_field_name})"
        )

        self.assertEqual(query, expected_query)

    def test_get_postgis_query_point_with_distance(self):
        operation = "touches"
        longitude, latitude = 1, 2
        distance = 10
        query = self.operator.get_postgis_query(operation, [[longitude, latitude]], distance)

        expected_query = (
            f"ST_Touches("
            f"ST_Buffer("
            f"ST_Transform("
            f"ST_SetSRID(ST_MakePoint({longitude}, {latitude}), {self.srid}), 3857), {distance}"
            f"), ST_Transform({self.gis_field_name}, 3857))"
        )

        self.assertEqual(query, expected_query)

    def test_get_postgis_query_line_with_distance(self):
        operation = "intersects"
        line = [[1, 2], [3, 4]]
        distance = 10
        query = self.operator.get_postgis_query(operation, line, distance, layer_type="line")

        expected_query = (
            f"ST_Intersects("
            f"ST_Buffer("
            f"ST_Transform("
            f"ST_SetSRID(ST_MakeLine(ARRAY[ST_MakePoint(1, 2), ST_MakePoint(3, 4)]), {self.srid}), 3857), {distance}"
            f"), ST_Transform({self.gis_field_name}, 3857))"
        )

        self.assertEqual(query, expected_query)

    def test_get_postgis_query_polygon_with_distance(self):
        operation = "contains"
        polygon = [[1, 2], [3, 4], [5, 6], [1, 2]]
        distance = 10
        query = self.operator.get_postgis_query(operation, polygon, distance, layer_type="polygon")

        expected_query = (
            f"ST_Contains("
            f"ST_Buffer("
            f"ST_Transform("
            f"ST_SetSRID(ST_MakePolygon(ST_MakeLine(ARRAY["
            f"ST_MakePoint(1, 2), "
            f"ST_MakePoint(3, 4), "
            f"ST_MakePoint(5, 6), "
            f"ST_MakePoint(1, 2)"
            f"])), {self.srid}), 3857), {distance}"
            f"), ST_Transform({self.gis_field_name}, 3857))"
        )

        self.assertEqual(query, expected_query)

    def test_get_postgis_query_invalid_operation(self):
        operation = "invalid"
        longitude, latitude = 1, 2

        with self.assertRaisesRegex(ValueError, f"Invalid operation: {operation}"):
            self.operator.get_postgis_query(operation, longitude, latitude)

    def test_clean_and_validate(self):
        with self.assertRaisesRegex(ValueError, "No keyword arguments provided."):
            self.operator.clean_and_validate()

        with self.assertRaisesRegex(ValueError, "Invalid operation: invalid"):
            self.operator.clean_and_validate(operation="invalid")

        coordinates = "invalid"
        with self.assertRaisesRegex(TypeError, f"Invalid coordinates: {coordinates}"):
            self.operator.clean_and_validate(coordinates=coordinates)

        coordinates = [1]
        with self.assertRaisesRegex(TypeError, f"Invalid coordinate: {coordinates[0]}"):
            self.operator.clean_and_validate(coordinates=coordinates)

        coordinates = [["one", 2]]
        with self.assertRaisesRegex(TypeError, f"Invalid coordinate: {', '.join(str(c) for c in coordinates[0])}"):
            self.operator.clean_and_validate(coordinates=coordinates)

        coordinates = [[1]]
        with self.assertRaisesRegex(ValueError, f"Invalid coordinate: {', '.join(str(c) for c in coordinates[0])}"):
            self.operator.clean_and_validate(coordinates=coordinates)

        coordinates = [[-181, 2]]
        with self.assertRaisesRegex(ValueError, f"Invalid coordinate: {', '.join(str(c) for c in coordinates[0])}"):
            self.operator.clean_and_validate(coordinates=coordinates)

        coordinates = [[-181, 2]]
        with self.assertRaisesRegex(ValueError, f"Invalid coordinate: {', '.join(str(c) for c in coordinates[0])}"):
            self.operator.clean_and_validate(coordinates=coordinates)

        coordinates = [[1, -91]]
        with self.assertRaisesRegex(ValueError, f"Invalid coordinate: {', '.join(str(c) for c in coordinates[0])}"):
            self.operator.clean_and_validate(coordinates=coordinates)

        coordinates = [[1, 91]]
        with self.assertRaisesRegex(ValueError, f"Invalid coordinate: {', '.join(str(c) for c in coordinates[0])}"):
            self.operator.clean_and_validate(coordinates=coordinates)

        layer_type = "invalid"
        with self.assertRaisesRegex(ValueError, f"Invalid layer type: {layer_type}"):
            self.operator.clean_and_validate(layer_type=layer_type)

        coordinates = [[1, 2]]
        layer_type = "polygon"
        with self.assertRaises(ValueError):
            self.operator.clean_and_validate(coordinates=coordinates, layer_type=layer_type)

        coordinates = [[1, 2], [3, 4]]
        layer_type = "point"

        with self.assertRaises(ValueError):
            self.operator.clean_and_validate(coordinates=coordinates, layer_type=layer_type)

        coordinates = [[1, 2], [3, 4]]
        layer_type = "polygon"
        with self.assertRaises(ValueError):
            self.operator.clean_and_validate(coordinates=coordinates, layer_type=layer_type)

        distance = "invalid"
        with self.assertRaisesRegex(TypeError, f"Invalid distance: {distance}"):
            self.operator.clean_and_validate(distance=distance)

    def test_st_makepoint(self):
        longitude, latitude = 1, 2
        point = self.operator.st_makepoint(longitude, latitude)

        self.assertEqual(point, f"ST_MakePoint({longitude}, {latitude})")

    def test_st_makeline(self):
        line = [[1, 2], [3, 4]]
        points = [self.operator.st_makepoint(*coord) for coord in line]
        line_string = self.operator.st_makeline(points)

        self.assertEqual(line_string, "ST_MakeLine(ARRAY[ST_MakePoint(1, 2), ST_MakePoint(3, 4)])")

    def test_st_makepolygon(self):
        polygon = [[1, 2], [3, 4], [5, 6], [1, 2]]
        points = [self.operator.st_makepoint(*coord) for coord in polygon]
        polygon_string = self.operator.st_makepolygon(points)

        expected_string = (
            "ST_MakePolygon(ST_MakeLine(ARRAY["
            "ST_MakePoint(1, 2), "
            "ST_MakePoint(3, 4), "
            "ST_MakePoint(5, 6), "
            "ST_MakePoint(1, 2)"
            "]))"
        )

        self.assertEqual(polygon_string, expected_string)

    def test_st_setsrid(self):
        point = "POINT(1 2)"
        srid = 3856
        point_result = self.operator.st_setsrid(point, srid)

        self.assertEqual(point_result, f"ST_SetSRID({point}, {srid})")
