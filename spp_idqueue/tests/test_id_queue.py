from datetime import date
from unittest.mock import Mock, patch

from odoo.exceptions import ValidationError

from .common import Common


class TestIdQueue(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_queue = cls._create_test_queue(registrant_id=cls._test_group.id, status="new")

    def test_01_compute_name(self):
        self.assertEqual(
            self.test_queue.name,
            "Shu clan - ID PASS Template",
            "Test queue should have the same name as `Shu clan - ID PASS Template`!",
        )

    def test_02_on_approve(self):
        self.assertListEqual(
            [
                self.test_queue.date_approved,
                self.test_queue.approved_by.id,
                self.test_queue.status,
            ],
            [False, False, "new"],
            "Test queue should not have those info in this state!",
        )
        self.test_queue.on_approve()
        self.assertListEqual(
            [
                self.test_queue.date_approved,
                self.test_queue.approved_by,
                self.test_queue.status,
            ],
            [date.today(), self.env.user, "approved"],
            "`on_approve` should add information into these fields!",
        )

    @patch("requests.post")
    def test_03_on_generate(self, mock_post):
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {"files": {"pdf": "1234567890123456789012345678TEST"}},
        )
        self.test_queue.status = "approved"
        self.assertListEqual(
            [
                self.test_queue.status,
                self.test_queue.generated_by.id,
                self.test_queue.date_generated,
            ],
            ["approved", False, False],
            "Test Queue status should be `approved`!",
        )
        self.test_queue.on_generate()
        self.assertListEqual(
            [
                self.test_queue.status,
                self.test_queue.generated_by,
                self.test_queue.date_generated,
            ],
            ["generated", self.env.user, date.today()],
            "Test Queue status should be `generated`!",
        )

    @patch("requests.post")
    def test_04_on_print(self, mock_post):
        with self.assertRaisesRegex(ValidationError, "^.*must be approved before printing$"):
            self.test_queue.on_print()
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {"files": {"pdf": "1234567890123456789012345678TEST"}},
        )
        self.test_queue.status = "approved"
        self.assertListEqual(
            [
                self.test_queue.status,
                self.test_queue.printed_by.id,
                self.test_queue.date_printed,
            ],
            ["approved", False, False],
            "Test Queue status should be `approved`!",
        )
        self.test_queue.on_print()
        self.assertListEqual(
            [
                self.test_queue.status,
                self.test_queue.printed_by,
                self.test_queue.date_printed,
            ],
            ["printed", self.env.user, date.today()],
            "Test Queue status should be `printed`!",
        )

    def test_05_on_distribute(self):
        with self.assertRaisesRegex(ValidationError, "^.*can only be distributed if it has been printed.*$"):
            self.test_queue.on_distribute()
        self.test_queue.status = "printed"
        self.assertListEqual(
            [
                self.test_queue.status,
                self.test_queue.distributed_by.id,
                self.test_queue.date_distributed,
            ],
            ["printed", False, False],
            "Test Queue status should be `printed`!",
        )
        self.test_queue.on_distribute()
        self.assertListEqual(
            [
                self.test_queue.status,
                self.test_queue.distributed_by,
                self.test_queue.date_distributed,
            ],
            ["distributed", self.env.user, date.today()],
            "Test Queue status should be `distributed`!",
        )

    def test_06_on_cancel_printed(self):
        self.test_queue.status = "printed"
        with self.assertRaisesRegex(ValidationError, "^.*cannot be canceled if it has been printed.*$"):
            self.test_queue.on_cancel()

    def test_07_on_cancel(self):
        self.test_queue.on_cancel()
        self.assertEqual(self.test_queue.status, "cancelled", "Test Queue should now `cancelled`!")
