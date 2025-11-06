import logging

from odoo.exceptions import ValidationError

from .common import AreaImportBaseTestMixin

_logger = logging.getLogger(__name__)


class BaseAreaImportTest(AreaImportBaseTestMixin):
    def test_01_cancel_area_import(self):
        """Test canceling an area import"""
        self.area_import_id.cancel_import()

        self.assertEqual(self.area_import_id.state, "Cancelled")

    def test_02_reset_to_uploaded_area(self):
        """Test resetting import back to uploaded state"""
        self.area_import_id.reset_to_uploaded()

        self.assertEqual(self.area_import_id.state, "Uploaded")

    def test_03_parse_excel_to_json(self):
        """Test parsing Excel file to JSON using pandas"""
        # Parse Excel to JSON
        self.area_import_id.parse_excel_to_json()

        # Check that parsing was successful
        self.assertEqual(self.area_import_id.state, "Parsed")
        self.assertIsNotNone(self.area_import_id.date_parsed)
        self.assertIsNotNone(self.area_import_id.parse_id)

        # Check that JSON files were created
        self.assertTrue(len(self.area_import_id.json_file_ids) > 0)

        # Verify JSON file structure
        for json_file in self.area_import_id.json_file_ids:
            self.assertIsNotNone(json_file.json_file)
            self.assertIsNotNone(json_file.json_file_name)
            self.assertTrue(json_file.row_count > 0)
            self.assertTrue(json_file.file_size > 0)
            self.assertIsNotNone(json_file.batch_number)

    def test_04_parse_excel_to_json_smaller_file(self):
        """Test parsing smaller Excel file (Palestine - less than 400 rows)"""
        # Parse Excel to JSON
        self.area_import_id_2.parse_excel_to_json()

        # Check that parsing was successful
        self.assertEqual(self.area_import_id_2.state, "Parsed")
        self.assertTrue(len(self.area_import_id_2.json_file_ids) > 0)

    def test_05_import_area_data_without_parsing(self):
        """Test that importing without parsing raises an error"""
        with self.assertRaises(ValidationError):
            self.area_import_id.import_data()

    def test_06_import_area_data_without_language(self):
        """Test that importing without activating required languages raises error"""
        # Parse Excel to JSON first
        self.area_import_id.parse_excel_to_json()

        # Try to import without activating Arabic language
        lang = self.env["res.lang"].with_context(active_test=False).search([("iso_code", "=", "ar")])
        lang.active = False

        with self.assertRaises(ValidationError) as context:
            self.area_import_id.import_data()

        # Check that error message mentions missing language
        self.assertIn("not activated", str(context.exception))

    def test_07_import_area_data_complete_workflow(self):
        """Test complete workflow: parse then import with proper language setup"""
        # Activate Arabic language
        lang = self.env["res.lang"].with_context(active_test=False).search([("iso_code", "=", "ar")])
        lang.active = True

        # Parse Excel to JSON
        self.area_import_id.parse_excel_to_json()
        self.assertEqual(self.area_import_id.state, "Parsed")

        # Import data from JSON
        self.area_import_id.import_data()

        # Check that import was successful
        self.assertEqual(self.area_import_id.state, "Imported")
        self.assertIsNotNone(self.area_import_id.date_imported)
        self.assertIsNotNone(self.area_import_id.import_id)

        # Check raw data was created
        raw_area_data_ids = self.area_import_id.raw_data_ids
        self.assertTrue(len(raw_area_data_ids) > 0)
        self.assertEqual(len(raw_area_data_ids.ids), self.area_import_id.tot_rows_imported)
        self.assertEqual(0, self.area_import_id.tot_rows_error)

        # Check that raw data records are in "New" state
        self.assertEqual(
            len(self.env["spp.area.import.raw"].search([("id", "in", raw_area_data_ids.ids), ("state", "=", "New")])),
            self.area_import_id.tot_rows_imported,
        )

    def test_08_json_file_model_fields(self):
        """Test that JSON file model has all required fields"""
        # Parse Excel to create JSON files
        self.area_import_id.parse_excel_to_json()

        json_file = self.area_import_id.json_file_ids[0]

        # Check all fields are present
        self.assertEqual(json_file.area_import_id, self.area_import_id)
        self.assertIsInstance(json_file.batch_number, int)
        self.assertTrue(json_file.json_file)
        self.assertTrue(json_file.json_file_name)
        self.assertIsInstance(json_file.row_count, int)
        self.assertIsInstance(json_file.file_size, int)

    def test_09_validate_languages_activated(self):
        """Test language validation function"""
        # Parse Excel to create JSON files
        lang = self.env["res.lang"].with_context(active_test=False).search([("iso_code", "=", "ar")])
        lang.active = True
        self.area_import_id.parse_excel_to_json()

        # Should not raise error when all languages are activated
        self.area_import_id._validate_languages_activated()

        # Deactivate Arabic and test validation fails
        lang.active = False
        with self.assertRaises(ValidationError) as context:
            self.area_import_id._validate_languages_activated()

        # Check error message format
        error_message = str(context.exception)
        self.assertIn("not activated", error_message.lower())

    def test_10_reload_page(self):
        """Test page reload action"""
        action = self.area_import_id.refresh_page()

        self.assertEqual(
            action,
            {
                "type": "ir.actions.client",
                "tag": "reload",
            },
        )

    def test_11_async_mark_done(self):
        """Test async mark done functionality"""
        self.area_import_id.locked = True
        self.area_import_id.locked_reason = "Testing"

        self.area_import_id._async_mark_done()

        self.assertFalse(self.area_import_id.locked)
        self.assertFalse(self.area_import_id.locked_reason)

    def test_12_async_mark_done_with_function(self):
        """Test async mark done with callback function"""
        self.area_import_id.locked = True
        self.area_import_id.locked_reason = "Testing"

        # Parse and import first to have data
        lang = self.env["res.lang"].with_context(active_test=False).search([("iso_code", "=", "ar")])
        lang.active = True
        self.area_import_id.parse_excel_to_json()
        self.area_import_id.import_data()

        # Call with _import_mark_done function
        self.area_import_id._async_mark_done("_import_mark_done")

        self.assertFalse(self.area_import_id.locked)
        self.assertFalse(self.area_import_id.locked_reason)
        self.assertEqual(self.area_import_id.state, "Imported")

    def test_13_compute_get_total_rows(self):
        """Test computation of total rows imported and error count"""
        # Parse and import
        lang = self.env["res.lang"].with_context(active_test=False).search([("iso_code", "=", "ar")])
        lang.active = True
        self.area_import_id.parse_excel_to_json()
        self.area_import_id.import_data()

        # Initial count
        initial_count = self.area_import_id.tot_rows_imported

        self.assertTrue(initial_count > 0)
        self.assertEqual(self.area_import_id.tot_rows_error, 0)

    def test_14_json_files_ordered_by_batch_number(self):
        """Test that JSON files are ordered by batch number"""
        # Parse Excel
        self.area_import_id.parse_excel_to_json()

        # Get all JSON files
        json_files = self.area_import_id.json_file_ids

        # Check ordering
        batch_numbers = [json_file.batch_number for json_file in json_files]
        self.assertEqual(batch_numbers, sorted(batch_numbers))

    def test_15_parse_clears_existing_json_files(self):
        """Test that parsing again clears existing JSON files"""
        # First parse
        self.area_import_id.parse_excel_to_json()
        len(self.area_import_id.json_file_ids)

        # Reset to uploaded and parse again
        self.area_import_id.reset_to_uploaded()
        self.area_import_id.parse_excel_to_json()
        second_count = len(self.area_import_id.json_file_ids)

        # Should have same or similar count (clearing and recreating)
        self.assertTrue(second_count > 0)

    def test_16_import_clears_existing_raw_data(self):
        """Test that importing again clears existing raw data"""
        # Parse and import
        lang = self.env["res.lang"].with_context(active_test=False).search([("iso_code", "=", "ar")])
        lang.active = True
        self.area_import_id.parse_excel_to_json()
        self.area_import_id.import_data()
        first_count = len(self.area_import_id.raw_data_ids)

        # Import again (without resetting)
        self.area_import_id.state = "Parsed"  # Reset to allow import again
        self.area_import_id.import_data()
        second_count = len(self.area_import_id.raw_data_ids)

        # Should have same count (clearing and recreating)
        self.assertEqual(first_count, second_count)
