from odoo.addons.spp_area.tests.test_area_import import AreaImportTest as AreaImportTestMixin


class AreaImportTest(AreaImportTestMixin):
    def test_get_column_indexes(self):
        columns = {
            "ADM2_EN": 0,
            "ADM2_PCODE": 1,
            "ADM1_EN": 2,
            "ADM1_PCODE": 3,
            "ADM0_EN": 4,
            "ADM0_PCODE": 5,
            "date": 6,
            "validOn": 7,
            "validTo": 8,
            "AREA_SQKM": 9,
            "longitude": 10,
            "latitude": 11,
        }
        area_level = 1
        column_indexes = self.area_import_id_2.get_column_indexes(list(columns.keys()), area_level)

        self.assertIn("latitude_index", column_indexes)
        self.assertIn("longitude_index", column_indexes)
        self.assertEqual(column_indexes["latitude_index"], columns["latitude"])
        self.assertEqual(column_indexes["longitude_index"], columns["longitude"])
