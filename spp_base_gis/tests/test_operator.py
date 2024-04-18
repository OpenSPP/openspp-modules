from odoo.tests.common import TransactionCase

from ..operators import Operator


class OperatorTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.gis_field_name = "geo_polygon_field"
        cls.gis_field = cls.env["spp.base.gis.test.model"]._fields[cls.gis_field_name]
        cls.srid = cls.gis_field.srid
        cls.operator = Operator(cls.gis_field)

    def test_create_point(self):
        longitude, latitude = 1, 2
        point = self.operator.create_point(longitude, latitude, self.srid)

        self.assertEqual(point, f"ST_SetSRID(ST_MakePoint({longitude}, {latitude}), {self.srid})")

    def test_st_transform(self):
        point = "POINT(1 2)"
        srid = 3856
        transformed_point = self.operator.st_transform(point, srid)

        self.assertEqual(transformed_point, f"ST_Transform({point}, {srid})")

    def test_get_postgis_query(self):
        operation = "touches"
        longitude, latitude = 1, 2
        query = self.operator.get_postgis_query(operation, longitude, latitude)

        self.assertEqual(
            query, f"ST_Touches(ST_SetSRID(ST_MakePoint({longitude}, {latitude}), {self.srid}), {self.gis_field_name})"
        )

    def test_get_postgis_query_with_distance(self):
        operation = "touches"
        longitude, latitude = 1, 2
        distance = 10
        query = self.operator.get_postgis_query(operation, longitude, latitude, distance)

        expected_query = (
            f"ST_Touches("
            f"ST_Buffer("
            f"ST_Transform("
            f"ST_SetSRID(ST_MakePoint({longitude}, {latitude}), {self.srid}), 3857), {distance}"
            f"), ST_Transform({self.gis_field_name}, 3857))"
        )

        self.assertEqual(query, expected_query)

    def test_get_postgis_query_invalid_operation(self):
        operation = "invalid"
        longitude, latitude = 1, 2

        with self.assertRaisesRegex(ValueError, f"Invalid operation: {operation}"):
            self.operator.get_postgis_query(operation, longitude, latitude)
