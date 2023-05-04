from datetime import date
from unittest.mock import Mock, patch

from odoo.exceptions import ValidationError

from .common import Common


class TestIdQueue(Common):
    def setUp(self):
        super().setUp()
        self.test_queue = self._create_test_queue(
            registrant_id=self._test_group.id, status="new"
        )

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
        with self.assertRaisesRegex(
            ValidationError, "^.*must be approved before printing$"
        ):
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
        with self.assertRaisesRegex(
            ValidationError, "^.*can only be distributed if it has been printed.*$"
        ):
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
        with self.assertRaisesRegex(
            ValidationError, "^.*cannot be canceled if it has been printed.*$"
        ):
            self.test_queue.on_cancel()

    def test_07_on_cancel(self):
        self.test_queue.on_cancel()
        self.assertEqual(
            self.test_queue.status, "cancelled", "Test Queue should now `cancelled`!"
        )

    def test_08_generate_cards(self):
        with self.assertRaisesRegex(
            ValidationError, "^.*must be approved before printing$"
        ):
            self.test_queue.generate_cards()

    def test_09_validate_requests(self):
        res = self.test_queue.validate_requests()
        self.assertRegex(
            res["params"]["message"],
            r"request\(s\) are validated\.$",
            "Should be an info message!",
        )
        self.assertEqual(res["params"]["type"], "info", "Should be an info message!")
        res = self.test_queue.validate_requests()
        self.assertEqual(
            res["params"]["message"],
            "Please select at least 1 new request which need to approve!",
            "Should be an warning message!",
        )
        self.assertEqual(
            res["params"]["type"], "warning", "Should be an warning message!"
        )

    def test_10_generate_validate_requests(self):
        self.test_queue.status = "new"
        res = self.test_queue.generate_validate_requests()
        self.assertEqual(
            res["params"]["message"],
            "Please select at least 1 approved request which need to generate!",
            "Should be an warning message!",
        )
        self.assertEqual(
            res["params"]["type"], "warning", "Should be an warning message!"
        )
        self.test_queue.status = "approved"
        res = self.test_queue.generate_validate_requests()
        jobs_created = self.env["queue.job"].search(
            [("model_name", "=", self.test_queue._name)]
        )
        self.assertTrue(
            bool(jobs_created.ids), "Should be jobs created for generating!"
        )
        self.assertRegex(
            res["params"]["message"],
            r"request\(s\) are now being generated\.$",
            "Should be an info message!",
        )
        self.assertEqual(res["params"]["type"], "info", "Should be an info message!")

    @patch("requests.post")
    def test_11_print_requests(self, mock_post):
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {"files": {"pdf": "1234567890123456789012345678TEST"}},
        )
        self.test_queue.status = "generated"
        res = self.test_queue.print_requests()
        self.assertRegex(
            res["params"]["message"],
            r"request\(s\) are printed\.$",
            "Should be an info message!",
        )
        self.assertEqual(res["params"]["type"], "info", "Should be an info message!")
        res = self.test_queue.print_requests()
        self.assertEqual(
            res["params"]["message"],
            "Please select at least 1 generated request which need to print!",
            "Should be an warning message!",
        )
        self.assertEqual(
            res["params"]["type"], "warning", "Should be an warning message!"
        )

    def test_12_distribute_requests(self):
        self.test_queue.status = "printed"
        res = self.test_queue.distribute_requests()
        self.assertRegex(
            res["params"]["message"],
            r"request\(s\) are distributed\.$",
            "Should be an info message!",
        )
        self.assertEqual(res["params"]["type"], "info", "Should be an info message!")
        res = self.test_queue.distribute_requests()
        self.assertEqual(
            res["params"]["message"],
            "Please select at least 1 printed request which need to distribute!",
            "Should be an warning message!",
        )
        self.assertEqual(
            res["params"]["type"], "warning", "Should be an warning message!"
        )

    def test_13_display_notification(self):
        res = self.test_queue._display_notification("1", "warning")
        self.assertEqual(res["params"]["message"], "1", "Should be an warning message!")
        self.assertEqual(
            res["params"]["type"], "warning", "Should be an warning message!"
        )
        self.assertEqual(
            res["type"], "ir.actions.client", "Should be an warning message!"
        )
        self.assertEqual(
            res["params"]["title"], "ID Requests", "Should be an warning message!"
        )
        self.assertTrue(res["params"]["sticky"], "Should be an warning message!")
