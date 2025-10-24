# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import base64
import json
import logging

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestDataImport(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set context to avoid job queue delay
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )

        # Create test data for import
        cls.test_partner_1 = cls.env["res.partner"].create(
            {
                "name": "Import Test Partner 1",
                "email": "import1@test.com",
            }
        )
        cls.test_partner_2 = cls.env["res.partner"].create(
            {
                "name": "Import Test Partner 2",
                "email": "import2@test.com",
            }
        )

        # Create sample export data
        cls.sample_export_data = [
            {"modules": ["base"]},
            {
                "model": "res.partner",
                "record_count": 2,
                "data": [
                    {
                        "id": 9991,
                        "name": "Test Import Partner A",
                        "email": "importa@test.com",
                        "active": True,
                    },
                    {
                        "id": 9992,
                        "name": "Test Import Partner B",
                        "email": "importb@test.com",
                        "active": True,
                    },
                ],
            },
        ]

        cls.sample_import_file = base64.b64encode(json.dumps(cls.sample_export_data).encode("utf-8"))

    def test_01_default_queue_job_minimum_size(self):
        """Test default queue job minimum size"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test Importer",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
            }
        )

        default_size = importer._default_queue_job_minimum_size()
        self.assertIsInstance(default_size, int)
        self.assertGreaterEqual(default_size, 0)

    def test_02_compute_total_number_of_models(self):
        """Test total number of models computation"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test Models Count",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
            }
        )

        importer._onchange_import_file()
        importer._compute_total_number_of_models()

        self.assertGreater(importer.total_number_of_models, 0)

    def test_03_compute_total_number_of_records(self):
        """Test total number of records computation"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test Records Count",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
            }
        )

        importer._onchange_import_file()
        importer._start_import()
        importer._compute_total_number_of_records()

        self.assertEqual(importer.total_number_of_records, 2)

    def test_04_compute_use_job_queue(self):
        """Test use_job_queue computation"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test Job Queue",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
                "queue_job_minimum_size": 1,
            }
        )

        importer._onchange_import_file()
        importer._start_import()
        importer._compute_use_job_queue()

        self.assertTrue(importer.use_job_queue)

    def test_05_onchange_import_file(self):
        """Test import file onchange"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test Onchange",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
            }
        )

        importer._onchange_import_file()

        self.assertIn("base", importer.module_list)
        self.assertIn("res.partner", importer.model_list)

    def test_06_start_import_parse_file(self):
        """Test start import and file parsing"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test Start Import",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
            }
        )

        importer._onchange_import_file()
        importer.start_import()

        # Check that raw data was created
        self.assertEqual(len(importer.raw_ids), 2)
        self.assertEqual(len(importer.summary_ids), 1)

    def test_07_start_import_internal(self):
        """Test internal start import method"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test Internal Import",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
            }
        )

        importer._start_import()

        # Verify raw records created
        self.assertEqual(len(importer.raw_ids), 2)
        self.assertTrue(all(raw.model_name == "res.partner" for raw in importer.raw_ids))

    def test_08_start_import_as_done(self):
        """Test import completion"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test Import Done",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
            }
        )

        importer._start_import()
        importer._start_import_as_done()

        self.assertEqual(importer.state, "imported")
        self.assertFalse(importer.locked)

    def test_09_validate_import_mapping(self):
        """Test validate import mapping"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test Validate Mapping",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
            }
        )

        importer._start_import()

        raw_mapping = {}
        importer._validate_import_mapping(raw_mapping)

        # Check that mapping was created
        self.assertTrue(len(raw_mapping) > 0)
        self.assertTrue(any("res.partner" in key for key in raw_mapping.keys()))

    def test_10_validate_import_json_update(self):
        """Test validate import JSON update"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test JSON Update",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
            }
        )

        importer._start_import()
        raw_mapping = {}
        importer._validate_import_mapping(raw_mapping)

        # Test JSON update for first raw record
        raw = importer.raw_ids[0]
        importer._validate_import_json_update(raw, raw_mapping)

        self.assertEqual(raw.state, "validated")
        self.assertTrue(raw.validated)

    def test_11_validate_import_full_process(self):
        """Test full validation process"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test Full Validation",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
            }
        )

        importer._start_import()
        importer._start_import_as_done()
        importer.validate_import()

        # All records should be validated
        validated_count = len(importer.raw_ids.filtered(lambda r: r.state == "validated"))
        self.assertEqual(validated_count, 2)

    def test_12_validate_import_as_done(self):
        """Test validation completion"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test Validation Done",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
            }
        )

        importer._start_import()
        importer._start_import_as_done()

        raw_mapping = json.loads(importer.raw_mapping_json or "{}")
        importer._validate_import_mapping(raw_mapping)

        for raw in importer.raw_ids:
            importer._validate_import(raw)

        message, kind = importer._validate_import_as_done()

        self.assertEqual(importer.state, "validated")
        self.assertTrue(importer.validated)
        self.assertEqual(kind, "success")

    def test_13_process_related_fields(self):
        """Test processing related fields"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test Related Fields",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
            }
        )

        model = self.env["res.partner"]
        json_data = {"id": 123, "name": "Test", "active": True}
        raw_mapping = {}

        updated_data = importer._process_related_fields(model, json_data, raw_mapping)

        # ID should be removed
        self.assertNotIn("id", updated_data)
        self.assertEqual(updated_data["name"], "Test")

    def test_14_process_many2one_field(self):
        """Test many2one field processing"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test Many2one",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
            }
        )

        # Create field mock
        field = self.env["res.partner"]._fields["company_id"]
        field_value = 123
        raw_mapping = {"res.company|123": 999}

        result = importer._process_many2one_field(field, field_value, raw_mapping)

        self.assertEqual(result, "raw:999")

    def test_15_process_x2many_field(self):
        """Test one2many/many2many field processing"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test X2many",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
            }
        )

        # Create field mock
        field = self.env["res.partner"]._fields["child_ids"]
        field_value = [123, 456]
        raw_mapping = {"res.partner|123": 888, "res.partner|456": 999}

        result = importer._process_x2many_field(field, field_value, raw_mapping)

        self.assertIsInstance(result, list)
        self.assertIn("raw:888", result)
        self.assertIn("raw:999", result)

    def test_16_check_skip_fields(self):
        """Test skip fields removal"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test Skip Fields",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
            }
        )

        json_data = {
            "name": "Test",
            "message_partner_ids": [1, 2, 3],
            "age": 25,
            "email": "test@example.com",
        }

        updated_data = importer._check_skip_fields(json_data)

        self.assertNotIn("message_partner_ids", updated_data)
        self.assertNotIn("age", updated_data)
        self.assertIn("name", updated_data)
        self.assertIn("email", updated_data)

    def test_17_create_records_simple(self):
        """Test simple record creation"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test Create Records",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
            }
        )

        importer._start_import()
        importer._start_import_as_done()
        importer.validate_import()

        importer.create_records()

        # Check that records were created
        created_count = len(importer.raw_ids.filtered(lambda r: r.state in ["created", "saved"]))
        self.assertGreater(created_count, 0)

    def test_18_create_single_record(self):
        """Test single record creation"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test Single Create",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
            }
        )

        importer._start_import()
        importer._start_import_as_done()
        importer.validate_import()

        created_mapping = {}
        raw = importer.raw_ids[0]

        record_id = importer._create_single_record(raw, created_mapping)

        self.assertIsNotNone(record_id)
        self.assertGreater(record_id, 0)

    def test_19_create_records_as_done(self):
        """Test create records completion"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test Create Done",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
            }
        )

        importer._start_import()
        importer._start_import_as_done()
        importer.validate_import()
        importer.create_records()

        message, kind = importer._create_records_as_done()

        self.assertEqual(importer.state, "completed")
        self.assertFalse(importer.locked)

    def test_20_check_existing_record(self):
        """Test existing record check"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test Existing Record",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
            }
        )

        # Create a record with known name
        existing_partner = self.env["res.partner"].create(
            {
                "name": "Existing Test Partner",
                "email": "existing@test.com",
            }
        )

        raw = self.env["spp.data.importer.raw"].create(
            {
                "name": "Test",
                "model_name": "res.partner",
                "importer_id": importer.id,
                "json_data": json.dumps({"name": "Existing Test Partner", "email": "existing@test.com"}),
            }
        )

        json_data = {"name": "Existing Test Partner", "email": "existing@test.com"}
        model = self.env["res.partner"]
        created_mapping = {}
        raw_ref = f"raw:{raw.id}"

        result = importer._check_existing_record(raw, json_data, model, created_mapping, raw_ref)

        # Should find existing record
        self.assertIsNotNone(result)
        self.assertEqual(result[0], existing_partner.id)

    def test_21_build_creation_data(self):
        """Test build creation data"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test Build Data",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
            }
        )

        raw = self.env["spp.data.importer.raw"].create(
            {
                "name": "Test",
                "model_name": "res.partner",
                "importer_id": importer.id,
                "json_data": json.dumps({"name": "New Partner", "email": "new@test.com"}),
            }
        )

        json_data = {"name": "New Partner", "email": "new@test.com"}
        model = self.env["res.partner"]
        created_mapping = {}
        _creating = set()

        creation_data, existing_id = importer._build_creation_data(raw, json_data, model, created_mapping, _creating)

        self.assertIn("name", creation_data)
        self.assertIn("email", creation_data)

    def test_22_create_process_datetime_field(self):
        """Test datetime field processing"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test Datetime",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
            }
        )

        # Test date field
        date_value = "2023-01-15"
        result_date = importer._create_process_datetime_field("date", date_value)
        self.assertEqual(result_date, "2023-01-15")

        # Test datetime field
        datetime_value = "2023-01-15T10:30:00"
        result_datetime = importer._create_process_datetime_field("datetime", datetime_value)
        self.assertEqual(result_datetime, "2023-01-15 10:30:00")

    def test_23_extract_raw_dependencies(self):
        """Test raw dependencies extraction"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test Dependencies",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
            }
        )

        data = {
            "name": "Test",
            "parent_id": "raw:123",
            "child_ids": ["raw:456", "raw:789"],
        }

        dependencies = importer._extract_raw_dependencies(data)

        self.assertIn(123, dependencies)
        self.assertIn(456, dependencies)
        self.assertIn(789, dependencies)
        self.assertEqual(len(dependencies), 3)

    def test_24_compute_module_ids(self):
        """Test module IDs computation"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test Module Compute",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
                "module_list": "base, mail",
            }
        )

        importer._compute_module_ids()

        self.assertTrue(importer.module_ids)
        self.assertGreater(len(importer.module_ids), 0)

    def test_25_compute_model_ids(self):
        """Test model IDs computation"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test Model Compute",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
                "model_list": "res.partner, res.users",
            }
        )

        importer._compute_model_ids()

        self.assertTrue(importer.model_ids)
        self.assertGreater(len(importer.model_ids), 0)

    def test_26_refresh_page(self):
        """Test refresh page action"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test Refresh",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
            }
        )

        result = importer.refresh_page()

        self.assertEqual(result["type"], "ir.actions.client")
        self.assertEqual(result["tag"], "reload")

    def test_27_importer_raw_model(self):
        """Test SPPDataImporterRaw model"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test Raw Model",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
            }
        )

        raw_record = self.env["spp.data.importer.raw"].create(
            {
                "name": "Test Raw",
                "model_name": "res.partner",
                "importer_id": importer.id,
                "record_id": 123,
                "json_data": "{}",
            }
        )

        self.assertEqual(raw_record.name, "Test Raw")
        self.assertEqual(raw_record.model_name, "res.partner")
        self.assertEqual(raw_record.record_id, 123)
        self.assertEqual(raw_record.state, "draft")
        self.assertFalse(raw_record.validated)

    def test_28_importer_summary_model(self):
        """Test SPPDataImporterSummary model"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test Summary Model",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
            }
        )

        summary_record = self.env["spp.data.importer.summary"].create(
            {
                "name": "res.partner",
                "importer_id": importer.id,
                "model_name": "res.partner",
                "record_count": 10,
            }
        )

        self.assertEqual(summary_record.name, "res.partner")
        self.assertEqual(summary_record.model_name, "res.partner")
        self.assertEqual(summary_record.record_count, 10)

    def test_29_importer_summary_compute_counts(self):
        """Test summary counts computation"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test Summary Counts",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
            }
        )

        # Create raw records with different states
        self.env["spp.data.importer.raw"].create(
            {
                "name": "Test 1",
                "model_name": "res.partner",
                "importer_id": importer.id,
                "json_data": "{}",
                "state": "created",
                "validated": True,
            }
        )
        self.env["spp.data.importer.raw"].create(
            {
                "name": "Test 2",
                "model_name": "res.partner",
                "importer_id": importer.id,
                "json_data": "{}",
                "state": "error",
                "validated": False,
            }
        )

        summary = self.env["spp.data.importer.summary"].create(
            {
                "name": "res.partner",
                "importer_id": importer.id,
                "model_name": "res.partner",
                "record_count": 2,
            }
        )

        summary._compute_counts()

        self.assertEqual(summary.success_count, 1)
        self.assertEqual(summary.error_count, 1)
        self.assertEqual(summary.validated_count, 1)

    def test_30_importer_summary_compute_state(self):
        """Test summary state computation"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test Summary State",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
            }
        )

        # Create summary with partial success
        self.env["spp.data.importer.raw"].create(
            {
                "name": "Success",
                "model_name": "res.partner",
                "importer_id": importer.id,
                "json_data": "{}",
                "state": "created",
            }
        )
        self.env["spp.data.importer.raw"].create(
            {
                "name": "Error",
                "model_name": "res.partner",
                "importer_id": importer.id,
                "json_data": "{}",
                "state": "error",
            }
        )

        summary = self.env["spp.data.importer.summary"].create(
            {
                "name": "res.partner",
                "importer_id": importer.id,
                "model_name": "res.partner",
                "record_count": 2,
            }
        )

        summary._compute_state()

        self.assertEqual(summary.state, "partial")

    def test_31_invalid_json_error_handling(self):
        """Test handling of invalid JSON"""
        invalid_json = base64.b64encode(b"not valid json")

        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test Invalid JSON",
                "import_file": invalid_json,
                "import_filename": "invalid.json",
            }
        )

        with self.assertRaises(ValidationError):
            importer._onchange_import_file()

    def test_32_state_transitions(self):
        """Test importer state transitions"""
        importer = self.env["spp.data.importer"].create(
            {
                "name": "Test State Transitions",
                "import_file": self.sample_import_file,
                "import_filename": "test.json",
            }
        )

        # Initial state
        self.assertEqual(importer.state, "draft")

        # After import
        importer._start_import()
        importer._start_import_as_done()
        self.assertEqual(importer.state, "imported")

        # After validation
        importer.validate_import()
        self.assertEqual(importer.state, "validated")

        # After creation
        importer.create_records()
        self.assertEqual(importer.state, "completed")
