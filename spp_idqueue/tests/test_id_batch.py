from datetime import date
from unittest.mock import Mock, patch

from odoo.exceptions import ValidationError

from .common import Common


class TestIdBatch(Common):
    def setUp(self):
        super().setUp()
        self._test_queue_1 = self._create_test_queue(self._test_individual_1.id)
        self._test_queue_2 = self._create_test_queue(self._test_individual_2.id)
        self._test_queue_3 = self._create_test_queue(self._test_individual_3.id)
        self.test_batch = self.env["spp.print.queue.batch"].create(
            {
                "name": "TEST BATCH 01",
                "queued_ids": [
                    (4, self._test_queue_1.id),
                    (4, self._test_queue_2.id),
                    (4, self._test_queue_3.id),
                ],
            }
        )

    def test_01_approve_batch(self):
        self.assertListEqual(
            [
                self.test_batch.status,
                self.test_batch.date_approved,
                self.test_batch.approved_by.id,
            ],
            ["new", False, False],
            "Test batch should be in `new` status!",
        )
        self.test_batch.approve_batch()
        self.assertListEqual(
            [
                self.test_batch.status,
                self.test_batch.date_approved,
                self.test_batch.approved_by,
            ],
            ["approved", date.today(), self.env.user],
            "Test batch should be in `approved` status!",
        )

    def test_02_mark_as_done_raise_error_01(self):
        with self.assertRaisesRegex(ValidationError, "Some IDs are not generated"):
            self.test_batch.mark_as_done(self.test_batch)

    def test_03_mark_as_done_raise_error_02(self):
        self.test_batch.queued_ids.write({"status": "generated"})
        with self.assertRaisesRegex(ValidationError, "No Auth Token or API URL"):
            self.test_batch.mark_as_done(self.test_batch)

    @patch("requests.post")
    def test_04_mark_as_done_response_403(self, mock_post):
        self.test_batch.queued_ids.write({"status": "generated"})
        template_batch_print = self.env.ref("spp_idqueue.id_template_batch_print")
        template_batch_print.write(
            {
                "auth_token": "AUTHENTIFICATION-TOKEN",
                "api_url": "http://127.0.0.1:8080/",
            }
        )
        mock_post.return_value = Mock(status_code=403)
        self.test_batch.mark_as_done(self.test_batch)
        self.assertEqual(
            self.test_batch.merge_status,
            "error_sending",
            "Merge status should be error, since the response status code is 403!",
        )
        self.assertEqual(
            self.test_batch.status, "generated", "Status should be generated!"
        )

    @patch("requests.post")
    def test_04_mark_as_done_response_200(self, mock_post):
        self.test_batch.queued_ids.write({"status": "generated"})
        template_batch_print = self.env.ref("spp_idqueue.id_template_batch_print")
        template_batch_print.write(
            {
                "auth_token": "AUTHENTIFICATION-TOKEN",
                "api_url": "http://127.0.0.1:8080/",
            }
        )
        mock_post.return_value = Mock(status_code=200)
        self.test_batch.mark_as_done(self.test_batch)
        self.assertEqual(
            self.test_batch.merge_status,
            "sent",
            "Merge status should be sent, since the response status code is 200!",
        )
        self.assertEqual(
            self.test_batch.status, "generated", "Status should be generated!"
        )

    def test_05_print_batch(self):
        self.assertEqual(self.test_batch.status, "new", "Status should be new!")
        self.test_batch.print_batch()
        self.assertEqual(
            self.test_batch.status, "printing", "Status should be printing!"
        )

    def test_06_batch_printed(self):
        self.assertEqual(self.test_batch.status, "new", "Status should be new!")
        self.assertListEqual(
            self.test_batch.queued_ids.mapped("status"),
            ["approved"] * 3,
            "All batch queues should in `approved`!",
        )
        self.test_batch.batch_printed()
        self.assertListEqual(
            [
                self.test_batch.status,
                self.test_batch.date_printed,
                self.test_batch.printed_by,
            ],
            ["printed", date.today(), self.env.user],
            "Test batch should be in `printed` status!",
        )
        for queue in self.test_batch.queued_ids:
            self.assertListEqual(
                [queue.status, queue.printed_by, queue.date_printed],
                ["printed", self.env.user, date.today()],
                "Test Queue status should be `printed`!",
            )

    def test_07_batch_distributed(self):
        self.assertEqual(self.test_batch.status, "new", "Status should be new!")
        self.assertListEqual(
            self.test_batch.queued_ids.mapped("status"),
            ["approved"] * 3,
            "All batch queues should in `approved`!",
        )
        self.test_batch.batch_distributed()
        self.assertListEqual(
            [
                self.test_batch.status,
                self.test_batch.date_distributed,
                self.test_batch.distributed_by,
            ],
            ["distributed", date.today(), self.env.user],
            "Test batch should be in `distributed` status!",
        )
        for queue in self.test_batch.queued_ids:
            self.assertListEqual(
                [queue.status, queue.distributed_by.id, queue.date_distributed],
                ["distributed", False, date.today()],
                "Test Queue status should be `distributed`!",
            )

    def test_08_generate_batch(self):
        self.test_batch._generate_batch(self.test_batch)
        for queue in self.test_batch.queued_ids:
            self.assertEqual(
                queue.status, "generating", "All queue should be generating!"
            )
        self.assertEqual(
            self.test_batch.status, "generating", "Batch should be generating!"
        )
        jobs_created = self.env["queue.job"].search(
            [("model_name", "=", self.test_batch._name)]
        )
        self.assertNotEqual(
            jobs_created.ids, [], "Should create jobs for generating batches!"
        )

    def test_09_multi_approve_batch(self):
        self.test_batch.status = "new"
        res = self.test_batch.multi_approve_batch()
        self.assertListEqual(
            [
                self.test_batch.date_approved,
                self.test_batch.approved_by.id,
                self.test_batch.status,
            ],
            [date.today(), self.env.uid, "approved"],
            "Test batch should be in `approved` status!",
        )
        self.assertRegex(
            res["params"]["message"],
            r"batch\(es\) are validated\.$",
            "Should be an info message!",
        )
        self.assertEqual(res["params"]["type"], "info", "Should be an info message!")
        res = self.test_batch.multi_approve_batch()
        self.assertEqual(
            res["params"]["message"],
            "Please select at least 1 new batch need to approve!",
            "Should be an warning message!",
        )
        self.assertEqual(
            res["params"]["type"], "warning", "Should be an warning message!"
        )

    def test_10_multi_print_batch(self):
        self.test_batch.write({"status": "generated", "merge_status": "merged"})
        res = self.test_batch.multi_print_batch()
        self.assertEqual(
            self.test_batch.status, "printing", "Batch status should be printing!"
        )
        self.assertRegex(
            res["params"]["message"],
            r"batch\(es\) are being printed\.$",
            "Should be an info message!",
        )
        self.assertEqual(res["params"]["type"], "info", "Should be an info message!")
        res = self.test_batch.multi_print_batch()
        self.assertEqual(
            res["params"]["message"],
            "Please select at least 1 generated batch need to print!",
            "Should be an warning message!",
        )
        self.assertEqual(
            res["params"]["type"], "warning", "Should be an warning message!"
        )

    def test_11_multi_printed_batch(self):
        self.test_batch.status = "printing"
        res = self.test_batch.multi_printed_batch()
        self.assertEqual(
            self.test_batch.status, "printed", "Batch status should be printed!"
        )
        self.assertEqual(
            self.test_batch.date_printed,
            date.today(),
            "Batch status should be printed!",
        )
        self.assertEqual(
            self.test_batch.printed_by.id,
            self.env.uid,
            "Batch status should be printed!",
        )
        for queue in self.test_batch.queued_ids:
            self.assertEqual(queue.status, "printed", "Queue status should be printed!")
            self.assertEqual(
                queue.date_printed, date.today(), "Queue status should be printed!"
            )
            self.assertEqual(
                queue.printed_by.id, self.env.uid, "Queue status should be printed!"
            )
        self.assertRegex(
            res["params"]["message"],
            r"batch\(es\) are printed\.$",
            "Should be an info message!",
        )
        self.assertEqual(res["params"]["type"], "info", "Should be an info message!")
        res = self.test_batch.multi_printed_batch()
        self.assertEqual(
            res["params"]["message"],
            "Please select at least 1 printing batch need to printed!",
            "Should be an warning message!",
        )
        self.assertEqual(
            res["params"]["type"], "warning", "Should be an warning message!"
        )

    def test_12_multi_distribute_batch(self):
        self.test_batch.status = "printed"
        res = self.test_batch.multi_distribute_batch()
        self.assertEqual(
            self.test_batch.status, "distributed", "Batch status should be distributed!"
        )
        self.assertEqual(
            self.test_batch.date_distributed,
            date.today(),
            "Batch status should be distributed!",
        )
        self.assertEqual(
            self.test_batch.distributed_by.id,
            self.env.uid,
            "Batch status should be distributed!",
        )
        for queue in self.test_batch.queued_ids:
            self.assertEqual(
                queue.status, "distributed", "Queue status should be distributed!"
            )
            self.assertEqual(
                queue.date_distributed,
                date.today(),
                "Queue status should be distributed!",
            )
        self.assertRegex(
            res["params"]["message"],
            r"batch\(es\) are distributed\.$",
            "Should be an info message!",
        )
        self.assertEqual(res["params"]["type"], "info", "Should be an info message!")
        res = self.test_batch.multi_distribute_batch()
        self.assertEqual(
            res["params"]["message"],
            "Please select at least 1 printed batch need to distribute!",
            "Should be an warning message!",
        )
        self.assertEqual(
            res["params"]["type"], "warning", "Should be an warning message!"
        )
