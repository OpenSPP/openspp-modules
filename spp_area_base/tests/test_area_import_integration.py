# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from .common import AreaImportBaseTestMixin

_logger = logging.getLogger(__name__)


class AreaImportIntegrationTest(AreaImportBaseTestMixin):
    """
    Integration tests for the complete area import workflow.
    Tests the full pipeline: Upload -> Parse -> Import -> Validate -> Save
    """

    def test_01_complete_workflow_small_file(self):
        """Test complete workflow with smaller file (Palestine)"""
        # Activate required language
        lang = self.env["res.lang"].with_context(active_test=False).search([("iso_code", "=", "ar")])
        lang.active = True

        # Step 1: File is uploaded (already done in setup)
        self.assertEqual(self.area_import_id_2.state, "Uploaded")

        # Step 2: Parse Excel to JSON
        self.area_import_id_2.parse_excel_to_json()
        self.assertEqual(self.area_import_id_2.state, "Parsed")
        self.assertTrue(len(self.area_import_id_2.json_file_ids) > 0)

        # Step 3: Import data from JSON
        self.area_import_id_2.import_data()
        self.assertEqual(self.area_import_id_2.state, "Imported")
        self.assertTrue(len(self.area_import_id_2.raw_data_ids) > 0)

        # Step 4: Validate raw data
        self.area_import_id_2.validate_raw_data()
        self.assertEqual(self.area_import_id_2.state, "Validated")

        # Step 5: Save to area
        self.area_import_id_2.save_to_area()
        self.assertEqual(self.area_import_id_2.state, "Done")

        # Verify areas were created
        for raw_data in self.area_import_id_2.raw_data_ids:
            self.assertTrue(raw_data.area_id, f"Area not created for {raw_data.admin_name}")
            self.assertEqual(raw_data.area_id.code, raw_data.admin_code)

    def test_02_workflow_state_transitions(self):
        """Test that state transitions follow the correct sequence"""
        # Activate required language
        lang = self.env["res.lang"].with_context(active_test=False).search([("iso_code", "=", "ar")])
        lang.active = True

        # Initial state
        self.assertEqual(self.area_import_id_2.state, "Uploaded")

        # Parse
        self.area_import_id_2.parse_excel_to_json()
        self.assertEqual(self.area_import_id_2.state, "Parsed")

        # Can reset to uploaded
        self.area_import_id_2.reset_to_uploaded()
        self.assertEqual(self.area_import_id_2.state, "Uploaded")

        # Parse again and continue
        self.area_import_id_2.parse_excel_to_json()
        self.area_import_id_2.import_data()
        self.assertEqual(self.area_import_id_2.state, "Imported")

        # Validate
        self.area_import_id_2.validate_raw_data()
        self.assertEqual(self.area_import_id_2.state, "Validated")

        # Save
        self.area_import_id_2.save_to_area()
        self.assertEqual(self.area_import_id_2.state, "Done")

    def test_03_locking_mechanism_during_operations(self):
        """Test that import is locked during long-running operations"""
        lang = self.env["res.lang"].with_context(active_test=False).search([("iso_code", "=", "ar")])
        lang.active = True

        # Parse - should set lock during operation
        self.area_import_id_2.parse_excel_to_json()
        # Lock should be released after completion
        self.assertFalse(self.area_import_id_2.locked)

        # Import - should set lock during operation
        self.area_import_id_2.import_data()
        # Lock should be released after completion
        self.assertFalse(self.area_import_id_2.locked)

    def test_04_multilevel_area_hierarchy(self):
        """Test that parent-child relationships are correctly established"""
        lang = self.env["res.lang"].with_context(active_test=False).search([("iso_code", "=", "ar")])
        lang.active = True

        # Complete workflow
        self.area_import_id_2.parse_excel_to_json()
        self.area_import_id_2.import_data()
        self.area_import_id_2.validate_raw_data()
        self.area_import_id_2.save_to_area()

        # Check that level 0 areas have no parent
        level_0_raw = self.area_import_id_2.raw_data_ids.filtered(lambda r: r.level == 0)
        for raw in level_0_raw:
            if raw.area_id:
                self.assertFalse(raw.area_id.parent_id, f"Level 0 area {raw.admin_name} should not have parent")

        # Check that level 1+ areas have parents
        level_1_raw = self.area_import_id_2.raw_data_ids.filtered(lambda r: r.level > 0)
        for raw in level_1_raw:
            if raw.area_id and raw.parent_code:
                # Parent should exist
                parent_area = self.env["spp.area"].search([("code", "=", raw.parent_code)], limit=1)
                self.assertTrue(parent_area, f"Parent area with code {raw.parent_code} not found")

    def test_05_translation_preservation(self):
        """Test that translations are preserved through the workflow"""
        lang_ar = self.env["res.lang"].with_context(active_test=False).search([("iso_code", "=", "ar")])
        lang_ar.active = True

        # Complete workflow
        self.area_import_id_2.parse_excel_to_json()
        self.area_import_id_2.import_data()
        self.area_import_id_2.validate_raw_data()
        self.area_import_id_2.save_to_area()

        # Check that areas have translations
        for raw in self.area_import_id_2.raw_data_ids:
            if raw.area_id:
                # English translation
                self.assertTrue(raw.area_id.draft_name)

                # Arabic translation (if available in source)
                area_ar = raw.area_id.with_context(lang="ar_001")
                self.assertTrue(area_ar.draft_name)

    def test_06_error_recovery_workflow(self):
        """Test recovery from errors during workflow"""
        lang = self.env["res.lang"].with_context(active_test=False).search([("iso_code", "=", "ar")])
        lang.active = True

        # Complete parse and import
        self.area_import_id_2.parse_excel_to_json()
        self.area_import_id_2.import_data()

        # Introduce an error in one raw record
        if self.area_import_id_2.raw_data_ids:
            error_record = self.area_import_id_2.raw_data_ids[0]
            error_record.admin_name = ""
            error_record.admin_code = ""

        # Validate - should mark record as error
        self.area_import_id_2.validate_raw_data()

        # State should not be Validated if there are errors
        if self.area_import_id_2.tot_rows_error > 0:
            self.assertNotEqual(self.area_import_id_2.state, "Validated")

        # Fix the error
        if self.area_import_id_2.raw_data_ids:
            error_record = self.area_import_id_2.raw_data_ids.filtered(lambda r: r.state == "Error")[0]
            error_record.admin_name = "Fixed Area"
            error_record.admin_code = "FIXED"

        # Validate again
        self.area_import_id_2.validate_raw_data()
        self.assertEqual(self.area_import_id_2.state, "Validated")

    def test_07_batch_processing_consistency(self):
        """Test that batch processing maintains data consistency"""
        lang = self.env["res.lang"].with_context(active_test=False).search([("iso_code", "=", "ar")])
        lang.active = True

        # Parse - creates batches
        self.area_import_id_2.parse_excel_to_json()

        # Count total rows in JSON batches
        total_json_rows = sum(json_file.row_count for json_file in self.area_import_id_2.json_file_ids)

        # Import
        self.area_import_id_2.import_data()

        # Count total imported rows
        total_imported = len(self.area_import_id_2.raw_data_ids)

        # Should match
        self.assertEqual(total_json_rows, total_imported, "JSON rows count should match imported rows count")

    def test_08_duplicate_code_handling(self):
        """Test handling of duplicate area codes"""
        lang = self.env["res.lang"].with_context(active_test=False).search([("iso_code", "=", "ar")])
        lang.active = True

        # Complete first import
        self.area_import_id_2.parse_excel_to_json()
        self.area_import_id_2.import_data()
        self.area_import_id_2.validate_raw_data()
        self.area_import_id_2.save_to_area()

        # Count areas created
        first_area_count = len(self.env["spp.area"].search([]))

        # Import same file again - should update existing areas
        # Create new import record with same file
        import base64

        file_path = self.get_file_path_pse()
        with open(file_path, "rb") as f:
            xls_file = base64.b64encode(f.read())

        new_import = self.env["spp.area.import"].create(
            {
                "excel_file": xls_file,
                "name": file_path,
                "state": "Uploaded",
            }
        )

        # Complete workflow
        new_import.parse_excel_to_json()
        new_import.import_data()
        new_import.validate_raw_data()
        new_import.save_to_area()

        # Area count should not significantly increase (duplicates updated)
        second_area_count = len(self.env["spp.area"].search([]))
        self.assertLessEqual(second_area_count, first_area_count * 1.1, "Duplicate import should update not create")

        # Check that records show as "Updated"
        updated_count = len(new_import.raw_data_ids.filtered(lambda r: r.state == "Updated"))
        self.assertTrue(updated_count > 0, "Some records should be marked as Updated")

    def test_09_cancel_workflow(self):
        """Test canceling import at various stages"""
        lang = self.env["res.lang"].with_context(active_test=False).search([("iso_code", "=", "ar")])
        lang.active = True

        # Cancel before parsing
        test_import = self.env["spp.area.import"].create(
            {
                "excel_file": self.area_import_id_2.excel_file,
                "name": "test_cancel.xlsx",
                "state": "Uploaded",
            }
        )
        test_import.cancel_import()
        self.assertEqual(test_import.state, "Cancelled")

        # Cancel after parsing
        test_import_2 = self.env["spp.area.import"].create(
            {
                "excel_file": self.area_import_id_2.excel_file,
                "name": "test_cancel_2.xlsx",
                "state": "Uploaded",
            }
        )
        test_import_2.parse_excel_to_json()
        test_import_2.cancel_import()
        self.assertEqual(test_import_2.state, "Cancelled")

    def test_10_performance_with_batching(self):
        """Test that batch processing works correctly for larger files"""
        lang = self.env["res.lang"].with_context(active_test=False).search([("iso_code", "=", "ar")])
        lang.active = True

        # Use the larger Iraq file
        self.area_import_id.parse_excel_to_json()

        # Check that multiple batches were created
        batch_count = len(self.area_import_id.json_file_ids)
        _logger.info(f"Created {batch_count} JSON batches for Iraq file")

        # Import
        self.area_import_id.import_data()

        # Check all batches were processed
        total_rows = sum(json_file.row_count for json_file in self.area_import_id.json_file_ids)
        imported_rows = len(self.area_import_id.raw_data_ids)

        self.assertEqual(total_rows, imported_rows, "All rows from all batches should be imported")
