from odoo.addons.spp_area.tests.test_area_import_raw import AreaImportRawTest as AreaImportRawTestMixin


class AreaImportRawTest(AreaImportRawTestMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.area_import_raw_id.latitude = 13.0
        cls.area_import_raw_id.longitude = 122.0

    def test_check_errors(self):
        self.area_import_raw_id.latitude = 91
        self.area_import_raw_id.longitude = 181

        self.area_import_raw_id.validate_raw_data()

        self.assertEqual(self.area_import_raw_id.state, "Error")
        self.assertIn("Latitude must be between -90 and 90", self.area_import_raw_id.remarks)
        self.assertIn("Longitude must be between -180 and 180", self.area_import_raw_id.remarks)

    def test_get_area_vals(self):
        area_vals = self.area_import_raw_id.get_area_vals()

        self.assertIn("coordinates", area_vals)
        self.assertEqual(area_vals["coordinates"], '{"type": "Point", "coordinates": [122.0, 13.0]}')
