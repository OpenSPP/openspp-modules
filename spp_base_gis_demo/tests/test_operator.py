import json

from shapely.geometry import Point

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
        point = self.operator.create_point([longitude, latitude], self.srid)

        self.assertEqual(point, f"ST_SetSRID(ST_MakePoint({longitude}, {latitude}), {self.srid})")

    def test_create_line(self):
        line = [[1, 2], [3, 4]]
        line_string = self.operator.create_line(line, self.srid)

        self.assertEqual(
            line_string, f"ST_SetSRID(ST_MakeLine(ARRAY[ST_MakePoint(1, 2), ST_MakePoint(3, 4)]), {self.srid})"
        )

    def test_create_polygon(self):
        polygon = [[[1, 2], [3, 4], [5, 6]]]
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
        query = self.operator.get_postgis_query(operation, [longitude, latitude])

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
        polygon = [[[1, 2], [3, 4], [5, 6], [1, 2]]]
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
        query = self.operator.get_postgis_query(operation, [longitude, latitude], distance)

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
        polygon = [[[1, 2], [3, 4], [5, 6], [1, 2]]]
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

        layer_type = "invalid"
        with self.assertRaisesRegex(ValueError, f"Invalid layer type: {layer_type}"):
            self.operator.clean_and_validate(layer_type=layer_type)

        coordinates = "invalid"
        with self.assertRaisesRegex(TypeError, f"Invalid coordinates: {coordinates}"):
            self.operator.clean_and_validate(coordinates=coordinates)

        distance = "invalid"
        with self.assertRaisesRegex(TypeError, f"Invalid distance: {distance}"):
            self.operator.clean_and_validate(distance=distance)

    def test_validate_coordinates_for_point(self):
        coordinates = [1]
        with self.assertRaisesRegex(ValueError, "Point coordinates should have 2 elements of type int or float."):
            self.operator.validate_coordinates_for_point(coordinates)

        coordinates = [1, "two"]
        with self.assertRaisesRegex(ValueError, "Point coordinates should have 2 elements of type int or float."):
            self.operator.validate_coordinates_for_point(coordinates)

        coordinates = ["two", 1]
        with self.assertRaisesRegex(ValueError, "Point coordinates should have 2 elements of type int or float."):
            self.operator.validate_coordinates_for_point(coordinates)

        coordinates = [-181, 2]
        with self.assertRaisesRegex(
            ValueError, "Longitude should be between -180 and 180, latitude should be between -90 and 90."
        ):
            self.operator.validate_coordinates_for_point(coordinates)

        coordinates = [181, 2]
        with self.assertRaisesRegex(
            ValueError, "Longitude should be between -180 and 180, latitude should be between -90 and 90."
        ):
            self.operator.validate_coordinates_for_point(coordinates)

        coordinates = [1, -91]
        with self.assertRaisesRegex(
            ValueError, "Longitude should be between -180 and 180, latitude should be between -90 and 90."
        ):
            self.operator.validate_coordinates_for_point(coordinates)

        coordinates = [1, 91]
        with self.assertRaisesRegex(
            ValueError, "Longitude should be between -180 and 180, latitude should be between -90 and 90."
        ):
            self.operator.validate_coordinates_for_point(coordinates)

        # Correct coordinates for point, must not have error
        coordinates = [1, 2]
        self.operator.validate_coordinates_for_point(coordinates)

    def test_validate_coordinates_for_line_or_polygon(self):
        coordinates = [1]
        with self.assertRaisesRegex(
            ValueError, "Line/Polygon coordinates should be tuples/lists with 2 elements of type int or float."
        ):
            self.operator.validate_coordinates_for_line_or_polygon(coordinates)

        coordinates = [[1]]
        with self.assertRaisesRegex(
            ValueError, "Line/Polygon coordinates should be tuples/lists with 2 elements of type int or float."
        ):
            self.operator.validate_coordinates_for_line_or_polygon(coordinates)

        coordinates = [[1, "two"]]
        with self.assertRaisesRegex(ValueError, "Line/Polygon longitude and latitude should be of type int or float."):
            self.operator.validate_coordinates_for_line_or_polygon(coordinates)

        coordinates = [["two", 1]]
        with self.assertRaisesRegex(ValueError, "Line/Polygon longitude and latitude should be of type int or float."):
            self.operator.validate_coordinates_for_line_or_polygon(coordinates)

        coordinates = [[-181, 2]]
        with self.assertRaisesRegex(
            ValueError, "Longitude should be between -180 and 180, latitude should be between -90 and 90."
        ):
            self.operator.validate_coordinates_for_line_or_polygon(coordinates)

        coordinates = [[181, 2]]
        with self.assertRaisesRegex(
            ValueError, "Longitude should be between -180 and 180, latitude should be between -90 and 90."
        ):
            self.operator.validate_coordinates_for_line_or_polygon(coordinates)

        coordinates = [[1, -91]]
        with self.assertRaisesRegex(
            ValueError, "Longitude should be between -180 and 180, latitude should be between -90 and 90."
        ):
            self.operator.validate_coordinates_for_line_or_polygon(coordinates)

        coordinates = [[1, 91]]
        with self.assertRaisesRegex(
            ValueError, "Longitude should be between -180 and 180, latitude should be between -90 and 90."
        ):
            self.operator.validate_coordinates_for_line_or_polygon(coordinates)

        coordinates = [[1, 2]]
        with self.assertRaisesRegex(ValueError, "Line coordinates should have at least 2 points."):
            self.operator.validate_coordinates_for_line_or_polygon(coordinates)

        with self.assertRaisesRegex(
            ValueError, "Polygon coordinates should have at least 4 points and start and end points must be the same."
        ):
            self.operator.validate_coordinates_for_line_or_polygon(coordinates, is_polygon=True)

        coordinates = [[1, 2], [3, 4], [5, 6], [7, 8]]
        with self.assertRaisesRegex(
            ValueError, "Polygon coordinates should have at least 4 points and start and end points must be the same."
        ):
            self.operator.validate_coordinates_for_line_or_polygon(coordinates, is_polygon=True)

        # Correct coordinates for line, must not have error
        coordinates = [[1, 2], [3, 4]]
        self.operator.validate_coordinates_for_line_or_polygon(coordinates)

        # Correct coordinates for polygon, must not have error
        coordinates = [[1, 2], [3, 4], [5, 6], [1, 2]]
        self.operator.validate_coordinates_for_line_or_polygon(coordinates, is_polygon=True)

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

    def test_domain_query(self):
        operator = "gis_intersects"

        value = 1
        with self.assertRaisesRegex(
            ValueError, "Value should be a geojson, WKT, a list or tuple with 2 elements, or a shapely geometry."
        ):
            self.operator.domain_query(operator, value)

        value = [1]
        with self.assertRaisesRegex(
            ValueError,
            "Value should be a list or tuple with 2 elements: a geojson/WKT/shapely geometry and a positive distance.",
        ):
            self.operator.domain_query(operator, value)

        value = [1, 2]
        with self.assertRaisesRegex(ValueError, "Invalid value type."):
            self.operator.domain_query(operator, value)

        value = ["geojson", "distance"]
        with self.assertRaisesRegex(
            ValueError,
            "Value should be a list or tuple with 2 elements: a geojson/WKT/shapely geometry and a positive distance.",
        ):
            self.operator.domain_query(operator, value)

        value = ["geojson", 0]
        with self.assertRaisesRegex(
            ValueError,
            "Value should be a list or tuple with 2 elements: a geojson/WKT/shapely geometry and a positive distance.",
        ):
            self.operator.domain_query(operator, value)

        value = "Invalid Geojson"
        with self.assertRaisesRegex(ValueError, "Invalid value: should be a geojson, WKT, or a shapely geometry."):
            self.operator.domain_query(operator, value)

        value = {"type": "Invalid", "coordinates": [1, 2]}
        with self.assertRaisesRegex(
            ValueError, "Invalid geojson type. Allowed types are Point, LineString, and Polygon."
        ):
            self.operator.domain_query(operator, value)

        value = {"type": "Point", "coordinates": [1]}
        with self.assertRaisesRegex(ValueError, "Invalid geojson."):
            self.operator.domain_query(operator, value)

        operator = "invalid_operator"
        value = {"type": "Point", "coordinates": [1, 2]}
        with self.assertRaisesRegex(ValueError, "Invalid operator."):
            self.operator.domain_query(operator, value)

        operator = "gis_intersects"

        # correct value (json), must not have error
        value = json.dumps({"type": "Point", "coordinates": [1, 2]})
        self.operator.domain_query(operator, value)

        # correct value (json) with distance, must not have error
        value = [value, 10]
        self.operator.domain_query(operator, value)

        # correct value (wkt), must not have error
        value = "POINT(1 2)"
        self.operator.domain_query(operator, value)

        # correct value (wkt) with distance, must not have error
        value = [value, 10]
        self.operator.domain_query(operator, value)

        # correct value (dict), must not have error
        value = {"type": "Point", "coordinates": [1, 2]}
        self.operator.domain_query(operator, value)

        # correct value (dict) with distance, must not have error
        value = [value, 10]
        self.operator.domain_query(operator, value)

        # correct value (shape), must not have error
        value = Point(1, 2)
        self.operator.domain_query(operator, value)
