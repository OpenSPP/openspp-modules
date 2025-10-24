# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import base64
import json
import logging

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestDataExport(TransactionCase):
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

        # Create a test model to export
        cls.test_model = cls.env["ir.model"].search([("model", "=", "res.partner")], limit=1)
        cls.test_module = cls.env["ir.module.module"].search(
            [("name", "=", "base"), ("state", "=", "installed")], limit=1
        )

        # Create test partner records
        cls.partner_1 = cls.env["res.partner"].create(
            {
                "name": "Test Partner 1",
                "email": "partner1@test.com",
            }
        )
        cls.partner_2 = cls.env["res.partner"].create(
            {
                "name": "Test Partner 2",
                "email": "partner2@test.com",
            }
        )

    def test_01_default_queue_job_minimum_size(self):
        """Test default queue job minimum size"""
        exporter = self.env["spp.data.exporter"].create(
            {
                "name": "Test Exporter",
            }
        )

        default_size = exporter._default_queue_job_minimum_size()
        self.assertIsInstance(default_size, int)
        self.assertGreaterEqual(default_size, 0)

    def test_02_compute_total_number_of_models(self):
        """Test total number of models computation"""
        exporter = self.env["spp.data.exporter"].create(
            {
                "name": "Test Models Count",
            }
        )

        # Manually set model_ids to test computation
        exporter.model_ids = [(6, 0, [self.test_model.id])]
        exporter._compute_total_number_of_models()

        self.assertEqual(exporter.total_number_of_models, 1)

    def test_03_compute_total_number_of_records(self):
        """Test total number of records computation"""
        exporter = self.env["spp.data.exporter"].create(
            {
                "name": "Test Records Count",
            }
        )

        exporter.model_ids = [(6, 0, [self.test_model.id])]
        exporter._compute_total_number_of_records()

        self.assertGreater(exporter.total_number_of_records, 0)

    def test_04_read_models_records(self):
        """Test reading model records"""
        exporter = self.env["spp.data.exporter"].create(
            {
                "name": "Test Read Records",
            }
        )

        exporter.model_ids = [(6, 0, [self.test_model.id])]
        exporter.read_models_records()

        # Check that raw data was created
        self.assertTrue(exporter.raw_ids)
        self.assertGreater(len(exporter.raw_ids), 0)

    def test_05_read_models_records_single_model(self):
        """Test reading single model records"""
        exporter = self.env["spp.data.exporter"].create(
            {
                "name": "Test Read Single Model",
            }
        )

        exporter._read_models_records(self.test_model)

        # Check that raw data was created
        self.assertTrue(exporter.raw_ids)
        raw_record = exporter.raw_ids[0]
        self.assertEqual(raw_record.name, self.test_model.model)
        self.assertEqual(raw_record.model_name, self.test_model.name)
        self.assertGreater(raw_record.record_count, 0)

    def test_06_start_export_sync(self):
        """Test synchronous export"""
        exporter = self.env["spp.data.exporter"].create(
            {
                "name": "Test Sync Export",
                "queue_job_minimum_size": 10000,  # High value to avoid job queue
            }
        )

        exporter.model_ids = [(6, 0, [self.test_model.id])]
        exporter.module_ids = [(6, 0, [self.test_module.id])]

        exporter.start_export()

        # Check export completed
        self.assertEqual(exporter.state, "completed")
        self.assertFalse(exporter.locked)
        self.assertTrue(exporter.export_file)
        self.assertTrue(exporter.export_filename)

    def test_07_mark_done(self):
        """Test mark done functionality"""
        exporter = self.env["spp.data.exporter"].create(
            {
                "name": "Test Mark Done",
            }
        )

        exporter.model_ids = [(6, 0, [self.test_model.id])]
        exporter.module_ids = [(6, 0, [self.test_module.id])]
        exporter.read_models_records()

        exporter._mark_done()

        # Check state and export file
        self.assertEqual(exporter.state, "completed")
        self.assertFalse(exporter.locked)
        self.assertTrue(exporter.export_file)
        self.assertTrue(exporter.export_filename)

        # Verify JSON structure
        json_data = json.loads(base64.b64decode(exporter.export_file).decode("utf-8"))
        self.assertIsInstance(json_data, list)
        self.assertTrue(len(json_data) > 0)
        self.assertIn("modules", json_data[0])

    def test_08_export_file_content_validation(self):
        """Test exported file content"""
        exporter = self.env["spp.data.exporter"].create(
            {
                "name": "Test Export Content",
                "queue_job_minimum_size": 10000,
            }
        )

        exporter.model_ids = [(6, 0, [self.test_model.id])]
        exporter.module_ids = [(6, 0, [self.test_module.id])]
        exporter.start_export()

        # Decode and validate export file
        export_data = base64.b64decode(exporter.export_file).decode("utf-8")
        json_data = json.loads(export_data)

        # Check structure
        self.assertIsInstance(json_data, list)
        self.assertGreater(len(json_data), 1)

        # Check modules section
        self.assertIn("modules", json_data[0])
        self.assertIsInstance(json_data[0]["modules"], list)

        # Check data section
        data_section = json_data[1]
        self.assertIn("model", data_section)
        self.assertIn("record_count", data_section)
        self.assertIn("data", data_section)
        self.assertEqual(data_section["model"], self.test_model.model)

    def test_09_refresh_page(self):
        """Test refresh page action"""
        exporter = self.env["spp.data.exporter"].create(
            {
                "name": "Test Refresh",
            }
        )

        result = exporter.refresh_page()

        self.assertEqual(result["type"], "ir.actions.client")
        self.assertEqual(result["tag"], "reload")

    def test_10_onchange_include_all_data(self):
        """Test include_all_data onchange"""
        exporter = self.env["spp.data.exporter"].create(
            {
                "name": "Test Include All",
            }
        )

        exporter.include_all_data = True
        exporter._onchange_include_all_data()

        self.assertTrue(exporter.include_installed_modules)

    def test_11_compute_module_ids_from_template(self):
        """Test module IDs computation from template"""
        # Create a template
        template = self.env["spp.data.exporter.templates"].create(
            {
                "name": "Test Template",
                "model_ids": [(6, 0, [self.test_model.id])],
            }
        )

        exporter = self.env["spp.data.exporter"].create(
            {
                "name": "Test Template Export",
                "template_id": template.id,
            }
        )

        exporter._compute_module_ids()

        self.assertTrue(exporter.module_ids)

    def test_12_compute_module_ids_include_all(self):
        """Test module IDs computation with include_installed_modules"""
        exporter = self.env["spp.data.exporter"].create(
            {
                "name": "Test Include All Modules",
                "include_installed_modules": True,
            }
        )

        exporter._compute_module_ids()

        # Should include all installed modules
        installed_count = self.env["ir.module.module"].search_count([("state", "=", "installed")])
        self.assertEqual(len(exporter.module_ids), installed_count)

    def test_13_compute_model_ids_from_template(self):
        """Test model IDs computation from template"""
        template = self.env["spp.data.exporter.templates"].create(
            {
                "name": "Test Template Models",
                "model_ids": [(6, 0, [self.test_model.id])],
            }
        )

        exporter = self.env["spp.data.exporter"].create(
            {
                "name": "Test Template Models Export",
                "template_id": template.id,
            }
        )

        exporter._compute_model_ids()

        self.assertTrue(exporter.model_ids)
        self.assertIn(self.test_model, exporter.model_ids)

    def test_14_compute_model_ids_include_all(self):
        """Test model IDs computation with include_all_data"""
        exporter = self.env["spp.data.exporter"].create(
            {
                "name": "Test Include All Data",
                "include_all_data": True,
            }
        )

        exporter._compute_model_ids()

        # Should include all non-transient models
        all_models_count = self.env["ir.model"].search_count([("transient", "=", False)])
        self.assertEqual(len(exporter.model_ids), all_models_count)

    def test_15_compute_use_job_queue(self):
        """Test use_job_queue computation"""
        # Small export
        small_exporter = self.env["spp.data.exporter"].create(
            {
                "name": "Small Export",
                "queue_job_minimum_size": 10000,
            }
        )
        small_exporter.model_ids = [(6, 0, [self.test_model.id])]
        small_exporter._compute_use_job_queue()

        # Large export
        large_exporter = self.env["spp.data.exporter"].create(
            {
                "name": "Large Export",
                "queue_job_minimum_size": 1,
            }
        )
        large_exporter.model_ids = [(6, 0, [self.test_model.id])]
        large_exporter._compute_use_job_queue()

        self.assertTrue(large_exporter.use_job_queue)

    def test_16_raw_exporter_model(self):
        """Test SPPDataExporterRaw model"""
        raw_record = self.env["spp.data.exporter.raw"].create(
            {
                "name": "res.partner",
                "model_name": "Contact",
                "record_count": 10,
                "json_data": "[]",
                "export_id": self.env["spp.data.exporter"].create({"name": "Test"}).id,
            }
        )

        self.assertEqual(raw_record.name, "res.partner")
        self.assertEqual(raw_record.model_name, "Contact")
        self.assertEqual(raw_record.record_count, 10)

    def test_17_export_template_model(self):
        """Test SPPDataExporterTemplates model"""
        template = self.env["spp.data.exporter.templates"].create(
            {
                "name": "Test Template",
                "model_ids": [(6, 0, [self.test_model.id])],
            }
        )

        self.assertEqual(template.name, "Test Template")
        self.assertTrue(template.active)
        self.assertIn(self.test_model, template.model_ids)

    def test_18_export_template_compute_module_ids(self):
        """Test template module IDs computation"""
        template = self.env["spp.data.exporter.templates"].create(
            {
                "name": "Test Template Modules",
                "model_ids": [(6, 0, [self.test_model.id])],
            }
        )

        template._compute_module_ids()

        # Should have computed modules from model
        self.assertTrue(template.module_ids)

    def test_19_related_fields(self):
        """Test related fields in exporter"""
        template = self.env["spp.data.exporter.templates"].create(
            {
                "name": "Test Related Fields",
                "model_ids": [(6, 0, [self.test_model.id])],
            }
        )

        exporter = self.env["spp.data.exporter"].create(
            {
                "name": "Test Related",
                "template_id": template.id,
            }
        )

        # Test related fields
        self.assertEqual(exporter.template_module_ids, template.module_ids)
        self.assertEqual(exporter.template_model_ids, template.model_ids)

    def test_20_export_with_binary_data(self):
        """Test export handles binary data correctly"""
        # Create a partner with image (binary field)
        self.env["res.partner"].create(
            {
                "name": "Partner with Image",
                "image_1920": base64.b64encode(b"fake_image_data"),
            }
        )

        exporter = self.env["spp.data.exporter"].create(
            {
                "name": "Test Binary Export",
                "queue_job_minimum_size": 10000,
            }
        )

        exporter.model_ids = [(6, 0, [self.test_model.id])]
        exporter.module_ids = [(6, 0, [self.test_module.id])]
        exporter.start_export()

        # Export should complete successfully
        self.assertEqual(exporter.state, "completed")
        self.assertTrue(exporter.export_file)

    def test_21_export_empty_model(self):
        """Test exporting a model with no records"""
        # Find or create a model with no records
        empty_model = self.env["ir.model"].search([("model", "=", "mail.test.gateway")], limit=1)
        if not empty_model:
            self.skipTest("Could not find suitable empty model for testing")

        exporter = self.env["spp.data.exporter"].create(
            {
                "name": "Test Empty Export",
                "queue_job_minimum_size": 10000,
            }
        )

        exporter._read_models_records(empty_model)

        # Should create raw record with empty data
        raw_record = exporter.raw_ids.filtered(lambda r: r.name == empty_model.model)
        if raw_record:
            self.assertEqual(raw_record.record_count, 0)
            self.assertEqual(raw_record.json_data, "[]")

    def test_22_state_transitions(self):
        """Test exporter state transitions"""
        exporter = self.env["spp.data.exporter"].create(
            {
                "name": "Test State Transitions",
                "queue_job_minimum_size": 10000,
            }
        )

        # Initial state
        self.assertEqual(exporter.state, "draft")
        self.assertFalse(exporter.locked)

        exporter.model_ids = [(6, 0, [self.test_model.id])]
        exporter.module_ids = [(6, 0, [self.test_module.id])]

        # Start export
        exporter.state = "in_progress"
        exporter.locked = True
        self.assertEqual(exporter.state, "in_progress")
        self.assertTrue(exporter.locked)

        # Complete export
        exporter.read_models_records()
        exporter._mark_done()
        self.assertEqual(exporter.state, "completed")
        self.assertFalse(exporter.locked)
