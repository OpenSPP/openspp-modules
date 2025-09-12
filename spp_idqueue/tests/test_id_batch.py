from datetime import date
from unittest.mock import Mock, patch

from odoo.exceptions import ValidationError

from .common import Common


class TestIdBatch(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.id_type = (
            cls.env["g2p.id.type"]
            .create(
                {
                    "name": "Test ID Type",
                }
            )
            .id
        )
        cls._test_queue_1 = cls._create_test_queue(cls._test_individual_1.id, cls.id_type)
        cls._test_queue_2 = cls._create_test_queue(cls._test_individual_2.id, cls.id_type)
        cls._test_queue_3 = cls._create_test_queue(cls._test_individual_3.id, cls.id_type)
        cls.test_batch = cls.env["spp.print.queue.batch"].create(
            {
                "name": "TEST BATCH 01",
                "queued_ids": [
                    (4, cls._test_queue_1.id),
                    (4, cls._test_queue_2.id),
                    (4, cls._test_queue_3.id),
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

    @patch("requests.post")
    def test_03_mark_as_done_response_200(self, mock_post):
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
            "merged",
            "Merge status should be merged, since this is not idpass!",
        )
        self.assertEqual(self.test_batch.status, "generated", "Status should be generated!")

    def test_04_print_batch(self):
        self.assertEqual(self.test_batch.status, "new", "Status should be new!")
        self.test_batch.print_batch()
        self.assertEqual(self.test_batch.status, "printing", "Status should be printing!")

    def test_05_batch_printed(self):
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

    def test_06_batch_distributed(self):
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
