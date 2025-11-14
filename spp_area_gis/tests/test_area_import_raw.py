# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import base64
import json
import logging

from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class AreaImportRawTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set context to avoid job queue delay for faster tests
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )

        # Create area import record
        cls.area_import_id = cls.env["spp.area.import"].create(
            {
                "excel_file": base64.b64encode(b"dummy_file"),
                "name": "test_gis_import.xlsx",
                "state": "Uploaded",
            }
        )

        # Create raw import record with GIS data
        cls.area_import_raw_id = cls.env["spp.area.import.raw"].create(
            {
                "area_import_id": cls.area_import_id.id,
                "admin_name": "Manila",
                "admin_code": "MNL",
                "parent_name": "Philippines",
                "parent_code": "PH",
                "level": 1,
                "area_sqkm": "200.23",
                "latitude": 13.0,
                "longitude": 122.0,
            }
        )

    def test_01_check_latitude_longitude_validation(self):
        """Test validation of latitude and longitude values"""
        # Test invalid latitude (> 90)
        self.area_import_raw_id.latitude = 91
        self.area_import_raw_id.longitude = 122.0

        self.area_import_raw_id.validate_raw_data()

        self.assertEqual(self.area_import_raw_id.state, "Error")
        self.assertIn("Latitude must be between -90 and 90", self.area_import_raw_id.remarks)

        # Reset and test invalid longitude (> 180)
        self.area_import_raw_id.latitude = 13.0
        self.area_import_raw_id.longitude = 181

        self.area_import_raw_id.validate_raw_data()

        self.assertEqual(self.area_import_raw_id.state, "Error")
        self.assertIn("Longitude must be between -180 and 180", self.area_import_raw_id.remarks)

    def test_02_check_latitude_without_longitude(self):
        """Test that latitude requires longitude"""
        self.area_import_raw_id.latitude = 89
        self.area_import_raw_id.longitude = False

        self.area_import_raw_id.validate_raw_data()

        self.assertEqual(self.area_import_raw_id.state, "Error")
        self.assertIn("Longitude is required if Latitude is provided", self.area_import_raw_id.remarks)

    def test_03_check_longitude_without_latitude(self):
        """Test that longitude requires latitude"""
        self.area_import_raw_id.latitude = False
        self.area_import_raw_id.longitude = 179

        self.area_import_raw_id.validate_raw_data()

        self.assertEqual(self.area_import_raw_id.state, "Error")
        self.assertIn("Latitude is required if Longitude is provided", self.area_import_raw_id.remarks)

    def test_04_valid_coordinates(self):
        """Test that valid coordinates pass validation"""
        self.area_import_raw_id.latitude = 13.0
        self.area_import_raw_id.longitude = 122.0

        self.area_import_raw_id.validate_raw_data()

        self.assertEqual(self.area_import_raw_id.state, "Validated")
        self.assertEqual(self.area_import_raw_id.remarks, "No Error")

    def test_05_get_area_vals_with_coordinates(self):
        """Test that get_area_vals generates correct GeoJSON coordinates"""
        self.area_import_raw_id.latitude = 13.0
        self.area_import_raw_id.longitude = 122.0

        area_vals = self.area_import_raw_id.get_area_vals()

        self.assertIn("coordinates", area_vals)
        self.assertEqual(area_vals["coordinates"], '{"type": "Point", "coordinates": [122.0, 13.0]}')

    def test_06_get_area_vals_without_coordinates(self):
        """Test that get_area_vals works without coordinates"""
        # Create record without coordinates
        raw_without_coords = self.env["spp.area.import.raw"].create(
            {
                "area_import_id": self.area_import_id.id,
                "admin_name": "Test Area",
                "admin_code": "TST",
                "level": 0,
                "area_sqkm": "100.0",
            }
        )

        area_vals = raw_without_coords.get_area_vals()

        # Should not have coordinates field
        self.assertNotIn("coordinates", area_vals)

    def test_07_negative_coordinates(self):
        """Test validation with negative but valid coordinates"""
        self.area_import_raw_id.latitude = -13.5
        self.area_import_raw_id.longitude = -122.5

        self.area_import_raw_id.validate_raw_data()

        self.assertEqual(self.area_import_raw_id.state, "Validated")
        self.assertEqual(self.area_import_raw_id.remarks, "No Error")

        # Check GeoJSON generation
        area_vals = self.area_import_raw_id.get_area_vals()
        self.assertEqual(area_vals["coordinates"], '{"type": "Point", "coordinates": [-122.5, -13.5]}')

    def test_08_boundary_coordinates(self):
        """Test validation at boundary values"""
        # Test max valid latitude
        self.area_import_raw_id.latitude = 90
        self.area_import_raw_id.longitude = 180

        self.area_import_raw_id.validate_raw_data()
        self.assertEqual(self.area_import_raw_id.state, "Validated")

        # Test min valid latitude
        self.area_import_raw_id.latitude = -90
        self.area_import_raw_id.longitude = -180

        self.area_import_raw_id.validate_raw_data()
        self.assertEqual(self.area_import_raw_id.state, "Validated")

    def test_09_import_data_from_json_with_gis(self):
        """Test that _import_data_from_json extracts latitude/longitude from JSON"""
        # Create area import for testing
        test_import = self.env["spp.area.import"].create(
            {
                "excel_file": base64.b64encode(b"dummy_file"),
                "name": "test_gis_json_import.xlsx",
                "state": "Parsed",
            }
        )

        # Create JSON data with GIS coordinates
        json_data = [
            {
                "_sheet_name": "ADM1",
                "_area_level": 1,
                "ADM1_EN": "Metro Manila",
                "ADM1_PCODE": "PH01",
                "ADM0_EN": "Philippines",
                "ADM0_PCODE": "PH",
                "AREA_SQKM": "619.57",
                "LATITUDE": 14.5995,
                "LONGITUDE": 120.9842,
            },
            {
                "_sheet_name": "ADM1",
                "_area_level": 1,
                "ADM1_EN": "Cebu",
                "ADM1_PCODE": "PH07",
                "ADM0_EN": "Philippines",
                "ADM0_PCODE": "PH",
                "AREA_SQKM": "4943.72",
                "LATITUDE": 10.3157,
                "LONGITUDE": 123.8854,
            },
        ]

        # Create JSON file record
        json_string = json.dumps(json_data)
        json_bytes = json_string.encode("utf-8")

        json_file = self.env["spp.area.import.json"].create(
            {
                "area_import_id": test_import.id,
                "batch_number": 0,
                "json_file_name": "batch_0.json",
                "json_file": base64.b64encode(json_bytes),
                "row_count": len(json_data),
                "file_size": len(json_bytes),
            }
        )

        # Call the import method
        test_import._import_data_from_json(json_file.id)

        # Verify raw records were created with GIS data
        raw_records = self.env["spp.area.import.raw"].search(
            [("area_import_id", "=", test_import.id)], order="admin_code"
        )

        self.assertEqual(len(raw_records), 2, "Should have created 2 raw records")

        # Check Cebu record (alphabetically first)
        cebu = raw_records[1]
        self.assertEqual(cebu.admin_code, "PH07")
        self.assertEqual(cebu.admin_name, "Cebu")
        self.assertAlmostEqual(cebu.latitude, 10.3157, places=4)
        self.assertAlmostEqual(cebu.longitude, 123.8854, places=4)
        self.assertEqual(cebu.level, 1)

        # Check Metro Manila record
        manila = raw_records[0]
        self.assertEqual(manila.admin_code, "PH01")
        self.assertEqual(manila.admin_name, "Metro Manila")
        self.assertAlmostEqual(manila.latitude, 14.5995, places=4)
        self.assertAlmostEqual(manila.longitude, 120.9842, places=4)
        self.assertEqual(manila.level, 1)

    def test_10_import_data_from_json_lowercase_gis_columns(self):
        """Test that _import_data_from_json handles lowercase latitude/longitude column names"""
        # Create area import for testing
        test_import = self.env["spp.area.import"].create(
            {
                "excel_file": base64.b64encode(b"dummy_file"),
                "name": "test_lowercase_gis.xlsx",
                "state": "Parsed",
            }
        )

        # Create JSON data with lowercase GIS coordinates
        json_data = [
            {
                "_sheet_name": "ADM1",
                "_area_level": 1,
                "ADM1_EN": "Davao",
                "ADM1_PCODE": "PH11",
                "ADM0_EN": "Philippines",
                "ADM0_PCODE": "PH",
                "AREA_SQKM": "20357.04",
                "latitude": 7.0731,
                "longitude": 125.6128,
            },
        ]

        # Create JSON file record
        json_string = json.dumps(json_data)
        json_bytes = json_string.encode("utf-8")

        json_file = self.env["spp.area.import.json"].create(
            {
                "area_import_id": test_import.id,
                "batch_number": 0,
                "json_file_name": "batch_0.json",
                "json_file": base64.b64encode(json_bytes),
                "row_count": len(json_data),
                "file_size": len(json_bytes),
            }
        )

        # Call the import method
        test_import._import_data_from_json(json_file.id)

        # Verify raw record was created with GIS data
        raw_record = self.env["spp.area.import.raw"].search([("area_import_id", "=", test_import.id)])

        self.assertEqual(len(raw_record), 1)
        self.assertEqual(raw_record.admin_code, "PH11")
        self.assertAlmostEqual(raw_record.latitude, 7.0731, places=4)
        self.assertAlmostEqual(raw_record.longitude, 125.6128, places=4)

    def test_11_import_data_from_json_without_gis(self):
        """Test that _import_data_from_json works without GIS coordinates"""
        # Create area import for testing
        test_import = self.env["spp.area.import"].create(
            {
                "excel_file": base64.b64encode(b"dummy_file"),
                "name": "test_no_gis.xlsx",
                "state": "Parsed",
            }
        )

        # Create JSON data without GIS coordinates
        json_data = [
            {
                "_sheet_name": "ADM0",
                "_area_level": 0,
                "ADM0_EN": "Philippines",
                "ADM0_PCODE": "PH",
                "AREA_SQKM": "300000.00",
            },
        ]

        # Create JSON file record
        json_string = json.dumps(json_data)
        json_bytes = json_string.encode("utf-8")

        json_file = self.env["spp.area.import.json"].create(
            {
                "area_import_id": test_import.id,
                "batch_number": 0,
                "json_file_name": "batch_0.json",
                "json_file": base64.b64encode(json_bytes),
                "row_count": len(json_data),
                "file_size": len(json_bytes),
            }
        )

        # Call the import method
        test_import._import_data_from_json(json_file.id)

        # Verify raw record was created without GIS data
        raw_record = self.env["spp.area.import.raw"].search([("area_import_id", "=", test_import.id)])

        self.assertEqual(len(raw_record), 1)
        self.assertEqual(raw_record.admin_code, "PH")
        self.assertFalse(raw_record.latitude, "Latitude should not be set")
        self.assertFalse(raw_record.longitude, "Longitude should not be set")
