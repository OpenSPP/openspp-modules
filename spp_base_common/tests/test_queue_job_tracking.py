# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import TransactionCase


class TestQueueJobTracking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.queue_job_model = cls.env["queue.job"]
        cls.area_import_model = cls.env["spp.area.import"]

        # Create test area import records
        cls.area_import_1 = cls.area_import_model.create(
            {
                "name": "Test Area Import 1",
            }
        )
        cls.area_import_2 = cls.area_import_model.create(
            {
                "name": "Test Area Import 2",
            }
        )

    def test_01_queue_job_res_fields(self):
        """Test that queue.job model has res_id and res_model fields"""
        job = self.queue_job_model.create(
            {
                "name": "Test Job",
                "model_name": "spp.area.import",
                "method_name": "test_method",
                "res_model": "spp.area.import",
                "res_id": self.area_import_1.id,
            }
        )

        self.assertEqual(job.res_model, "spp.area.import")
        self.assertEqual(job.res_id, self.area_import_1.id)

    def test_02_compute_job_ids(self):
        """Test that area import correctly computes related jobs"""
        # Create jobs for area_import_1
        job1 = self.queue_job_model.create(
            {
                "name": "Job 1 for Import 1",
                "model_name": "spp.area.import",
                "method_name": "test_method",
                "res_model": "spp.area.import",
                "res_id": self.area_import_1.id,
                "state": "done",
            }
        )
        job2 = self.queue_job_model.create(
            {
                "name": "Job 2 for Import 1",
                "model_name": "spp.area.import",
                "method_name": "test_method",
                "res_model": "spp.area.import",
                "res_id": self.area_import_1.id,
                "state": "pending",
            }
        )

        # Create job for area_import_2
        job3 = self.queue_job_model.create(
            {
                "name": "Job 1 for Import 2",
                "model_name": "spp.area.import",
                "method_name": "test_method",
                "res_model": "spp.area.import",
                "res_id": self.area_import_2.id,
                "state": "done",
            }
        )

        # Trigger compute
        self.area_import_1._compute_job_ids()
        self.area_import_2._compute_job_ids()

        # Assert area_import_1 has 2 jobs
        self.assertEqual(len(self.area_import_1.job_ids), 2)
        self.assertIn(job1, self.area_import_1.job_ids)
        self.assertIn(job2, self.area_import_1.job_ids)
        self.assertNotIn(job3, self.area_import_1.job_ids)

        # Assert area_import_2 has 1 job
        self.assertEqual(len(self.area_import_2.job_ids), 1)
        self.assertIn(job3, self.area_import_2.job_ids)
        self.assertNotIn(job1, self.area_import_2.job_ids)
        self.assertNotIn(job2, self.area_import_2.job_ids)

    def test_03_has_ongoing_jobs_no_jobs(self):
        """Test has_ongoing_jobs when there are no jobs"""
        self.area_import_1._compute_has_ongoing_jobs()
        self.area_import_2._compute_has_ongoing_jobs()

        self.assertFalse(self.area_import_1.has_ongoing_jobs)
        self.assertFalse(self.area_import_2.has_ongoing_jobs)

    def test_04_has_ongoing_jobs_with_pending_job(self):
        """Test has_ongoing_jobs when there is a pending job"""
        # Create a pending job
        self.queue_job_model.create(
            {
                "name": "Pending Job",
                "model_name": "spp.area.import",
                "method_name": "test_method",
                "res_model": "spp.area.import",
                "res_id": self.area_import_1.id,
                "state": "pending",
            }
        )

        # Trigger compute on both records
        self.area_import_1._compute_has_ongoing_jobs()
        self.area_import_2._compute_has_ongoing_jobs()

        # Both should show has_ongoing_jobs = True because it checks the entire model
        self.assertTrue(self.area_import_1.has_ongoing_jobs)
        self.assertTrue(self.area_import_2.has_ongoing_jobs)

    def test_05_has_ongoing_jobs_with_enqueued_job(self):
        """Test has_ongoing_jobs when there is an enqueued job"""
        # Clean up previous jobs
        self.queue_job_model.search([("res_model", "=", "spp.area.import")]).unlink()

        # Create an enqueued job
        self.queue_job_model.create(
            {
                "name": "Enqueued Job",
                "model_name": "spp.area.import",
                "method_name": "test_method",
                "res_model": "spp.area.import",
                "res_id": self.area_import_2.id,
                "state": "enqueued",
            }
        )

        # Trigger compute
        self.area_import_1._compute_has_ongoing_jobs()
        self.area_import_2._compute_has_ongoing_jobs()

        # Both should show has_ongoing_jobs = True
        self.assertTrue(self.area_import_1.has_ongoing_jobs)
        self.assertTrue(self.area_import_2.has_ongoing_jobs)

    def test_06_has_ongoing_jobs_with_started_job(self):
        """Test has_ongoing_jobs when there is a started job"""
        # Clean up previous jobs
        self.queue_job_model.search([("res_model", "=", "spp.area.import")]).unlink()

        # Create a started job
        self.queue_job_model.create(
            {
                "name": "Started Job",
                "model_name": "spp.area.import",
                "method_name": "test_method",
                "res_model": "spp.area.import",
                "res_id": self.area_import_1.id,
                "state": "started",
            }
        )

        # Trigger compute
        self.area_import_1._compute_has_ongoing_jobs()
        self.area_import_2._compute_has_ongoing_jobs()

        # Both should show has_ongoing_jobs = True
        self.assertTrue(self.area_import_1.has_ongoing_jobs)
        self.assertTrue(self.area_import_2.has_ongoing_jobs)

    def test_07_has_ongoing_jobs_with_done_job(self):
        """Test has_ongoing_jobs when all jobs are done"""
        # Clean up previous jobs
        self.queue_job_model.search([("res_model", "=", "spp.area.import")]).unlink()

        # Create only done/failed jobs
        self.queue_job_model.create(
            {
                "name": "Done Job",
                "model_name": "spp.area.import",
                "method_name": "test_method",
                "res_model": "spp.area.import",
                "res_id": self.area_import_1.id,
                "state": "done",
            }
        )
        self.queue_job_model.create(
            {
                "name": "Failed Job",
                "model_name": "spp.area.import",
                "method_name": "test_method",
                "res_model": "spp.area.import",
                "res_id": self.area_import_2.id,
                "state": "failed",
            }
        )

        # Trigger compute
        self.area_import_1._compute_has_ongoing_jobs()
        self.area_import_2._compute_has_ongoing_jobs()

        # Both should show has_ongoing_jobs = False
        self.assertFalse(self.area_import_1.has_ongoing_jobs)
        self.assertFalse(self.area_import_2.has_ongoing_jobs)

    def test_08_has_ongoing_jobs_mixed_states(self):
        """Test has_ongoing_jobs with mixed job states"""
        # Clean up previous jobs
        self.queue_job_model.search([("res_model", "=", "spp.area.import")]).unlink()

        # Create jobs with different states
        self.queue_job_model.create(
            {
                "name": "Done Job",
                "model_name": "spp.area.import",
                "method_name": "test_method",
                "res_model": "spp.area.import",
                "res_id": self.area_import_1.id,
                "state": "done",
            }
        )
        self.queue_job_model.create(
            {
                "name": "Pending Job",
                "model_name": "spp.area.import",
                "method_name": "test_method",
                "res_model": "spp.area.import",
                "res_id": self.area_import_2.id,
                "state": "pending",
            }
        )

        # Trigger compute
        self.area_import_1._compute_has_ongoing_jobs()
        self.area_import_2._compute_has_ongoing_jobs()

        # Both should show has_ongoing_jobs = True because there's one pending job
        self.assertTrue(self.area_import_1.has_ongoing_jobs)
        self.assertTrue(self.area_import_2.has_ongoing_jobs)

    def test_09_job_ids_empty_for_different_model(self):
        """Test that job_ids is empty when jobs belong to different model"""
        # Create a job with different res_model
        self.queue_job_model.create(
            {
                "name": "Job for different model",
                "model_name": "res.partner",
                "method_name": "test_method",
                "res_model": "res.partner",
                "res_id": 1,
                "state": "done",
            }
        )

        # Trigger compute
        self.area_import_1._compute_job_ids()

        # Should not include jobs from other models
        self.assertEqual(len(self.area_import_1.job_ids), 0)

    def test_10_has_ongoing_jobs_different_model(self):
        """Test that has_ongoing_jobs is not affected by jobs from different models"""
        # Clean up previous jobs
        self.queue_job_model.search([("res_model", "=", "spp.area.import")]).unlink()

        # Create a pending job for a different model
        self.queue_job_model.create(
            {
                "name": "Job for different model",
                "model_name": "res.partner",
                "method_name": "test_method",
                "res_model": "res.partner",
                "res_id": 1,
                "state": "pending",
            }
        )

        # Trigger compute
        self.area_import_1._compute_has_ongoing_jobs()

        # Should not be affected by jobs from other models
        self.assertFalse(self.area_import_1.has_ongoing_jobs)
