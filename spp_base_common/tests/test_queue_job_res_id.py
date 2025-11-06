# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestQueueJobResId(TransactionCase):
    """Test automatic population of res_id in queue jobs."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set context to avoid job queue delay for testing
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )

    def test_01_single_record_job_creation(self):
        """Test that res_id is populated when a single record creates a job."""
        # Create a test partner record
        partner = self.env["res.partner"].create(
            {
                "name": "Test Partner for Queue Job",
                "email": "test@example.com",
            }
        )

        # Create a method that can be delayed (using existing method)
        # We'll use a simple method that exists on res.partner
        job = partner.with_delay().write({"phone": "1234567890"})

        # Verify job was created
        self.assertTrue(job, "Job should be created")

        # Get the queue.job record
        queue_job = self.env["queue.job"].search([("uuid", "=", job.uuid)], limit=1)

        # Verify res_id is populated correctly
        self.assertEqual(
            queue_job.res_id,
            partner.id,
            "res_id should be set to the partner ID",
        )
        self.assertEqual(
            queue_job.res_model,
            "res.partner",
            "res_model should be set to res.partner",
        )
        self.assertEqual(
            queue_job.model_name,
            "res.partner",
            "model_name should be res.partner",
        )

    def test_02_multiple_records_job_creation(self):
        """Test that res_id is populated when multiple records create a job."""
        # Create multiple test partner records
        partners = self.env["res.partner"].create(
            [
                {"name": "Test Partner 1", "email": "test1@example.com"},
                {"name": "Test Partner 2", "email": "test2@example.com"},
                {"name": "Test Partner 3", "email": "test3@example.com"},
            ]
        )

        # Create a job with multiple records
        job = partners.with_delay().write({"phone": "9876543210"})

        # Verify job was created
        self.assertTrue(job, "Job should be created")

        # Get the queue.job record
        queue_job = self.env["queue.job"].search([("uuid", "=", job.uuid)], limit=1)

        # Verify res_id is populated with first record's ID
        self.assertEqual(
            queue_job.res_id,
            partners[0].id,
            "res_id should be set to the first partner ID",
        )
        self.assertEqual(
            queue_job.res_model,
            "res.partner",
            "res_model should be set to res.partner",
        )

    def test_03_res_id_field_indexed(self):
        """Test that res_id field is indexed for performance."""
        # Get the field information
        field = self.env["queue.job"]._fields.get("res_id")

        # Verify field exists and is indexed
        self.assertTrue(field, "res_id field should exist")
        self.assertTrue(field.index, "res_id field should be indexed")

    def test_04_res_model_field_indexed(self):
        """Test that res_model field is indexed for performance."""
        # Get the field information
        field = self.env["queue.job"]._fields.get("res_model")

        # Verify field exists and is indexed
        self.assertTrue(field, "res_model field should exist")
        self.assertTrue(field.index, "res_model field should be indexed")

    def test_05_search_jobs_by_res_id(self):
        """Test searching for jobs by res_id."""
        # Create a test partner record
        partner = self.env["res.partner"].create(
            {
                "name": "Test Partner for Search",
                "email": "search@example.com",
            }
        )

        # Create multiple jobs for the same partner
        job1 = partner.with_delay().write({"phone": "1111111111"})
        job2 = partner.with_delay().write({"mobile": "2222222222"})

        # Search for jobs by res_id
        jobs = self.env["queue.job"].search(
            [
                ("res_id", "=", partner.id),
                ("res_model", "=", "res.partner"),
            ]
        )

        # Verify we found at least the jobs we created
        job_uuids = jobs.mapped("uuid")
        self.assertIn(
            job1.uuid,
            job_uuids,
            "Should find first job by res_id",
        )
        self.assertIn(
            job2.uuid,
            job_uuids,
            "Should find second job by res_id",
        )
