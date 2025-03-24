from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestSPPAttendance(TransactionCase):
    def setUp(self):
        super().setUp()
        # Set up test data
        self.env = self.env(context=dict(self.env.context, tracking_disable=True))

        # Create test user
        self.test_user = self.env["res.users"].create(
            {
                "name": "Test User",
                "login": "test_user",
                "email": "test@example.com",
            }
        )

        # Create test registrant
        self.test_registrant = self.env["res.partner"].create(
            {
                "name": "Test Registrant",
            }
        )

        # Create test program
        self.test_program = self.env["g2p.program"].create(
            {
                "name": "Test Program",
                "program_membership_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": self.test_registrant.id,
                        },
                    )
                ],
            }
        )

    def test_create_attendance(self):
        """Test creating an attendance record"""
        attendance = self.env["g2p.attendance"].create(
            {
                "registrant_id": self.test_registrant.id,
                "program_id": self.test_program.id,
                "state": "draft",
            }
        )

        self.assertEqual(attendance.state, "draft")
        self.assertEqual(attendance.registrant_id, self.test_registrant)
        self.assertEqual(attendance.program_id, self.test_program)

    def test_attendance_validation(self):
        """Test attendance validation rules"""
        # Test creating attendance without required fields
        with self.assertRaises(ValidationError):
            self.env["g2p.attendance"].create(
                {
                    "state": "draft",
                }
            )

    def test_attendance_state_changes(self):
        """Test attendance state transitions"""
        attendance = self.env["g2p.attendance"].create(
            {
                "registrant_id": self.test_registrant.id,
                "program_id": self.test_program.id,
                "state": "draft",
            }
        )

        # Test confirm action
        attendance.action_confirm()
        self.assertEqual(attendance.state, "confirmed")

        # Test cancel action
        attendance.action_cancel()
        self.assertEqual(attendance.state, "cancelled")

        # Test reset to draft
        attendance.action_draft()
        self.assertEqual(attendance.state, "draft")

    def test_compute_display_name(self):
        """Test the display name computation"""
        attendance = self.env["g2p.attendance"].create(
            {
                "registrant_id": self.test_registrant.id,
                "program_id": self.test_program.id,
                "state": "draft",
            }
        )

        expected_name = f"{self.test_registrant.name} - {self.test_program.name}"
        self.assertEqual(attendance.display_name, expected_name)
