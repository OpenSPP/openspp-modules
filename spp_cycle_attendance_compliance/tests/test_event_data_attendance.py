from datetime import datetime, timedelta

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestEventDataAttendance(TransactionCase):
    def setUp(self):
        super().setUp()
        # Create test data
        self.program = self.env["g2p.program"].create(
            {
                "name": "Test Program",
                "program_membership_ids": [(0, 0, {"name": "Test Program Membership"})],
            }
        )

        self.cycle = self.env["g2p.cycle"].create(
            {
                "name": "Test Cycle",
                "program_id": self.program.id,
                "start_date": datetime.now(),
                "end_date": datetime.now() + timedelta(days=30),
            }
        )

        self.individual = self.env["res.partner"].create(
            {
                "name": "Test Individual",
                "is_registrant": True,
            }
        )

        self.event = self.env["spp.event.data"].create(
            {
                "name": "Test Event",
                "date_start": datetime.now(),
                "date_end": datetime.now() + timedelta(days=1),
                "model": "g2p.cycle.membership.attendance",
                "partner_id": self.individual.id,  # Required field
            }
        )

    def test_01_create_event_attendance(self):
        """Test creating event attendance"""
        event_attendance = self.env["spp.event.data.attendance"].create(
            {
                "event_id": self.event.id,
                "registrant_id": self.individual.id,
                "attendance_date": datetime.now(),
            }
        )

        self.assertTrue(event_attendance, "Event attendance should be created")
        self.assertEqual(event_attendance.state, "draft", "Initial state should be draft")

    def test_02_validate_event_attendance(self):
        """Test event attendance validation"""
        event_attendance = self.env["spp.event.data.attendance"].create(
            {
                "event_id": self.event.id,
                "registrant_id": self.individual.id,
                "attendance_date": datetime.now(),
            }
        )

        event_attendance.action_validate()
        self.assertEqual(event_attendance.state, "validated", "State should be validated after validation")

    def test_03_duplicate_event_attendance(self):
        """Test duplicate event attendance validation"""
        with self.assertRaises(ValidationError):
            self.env["spp.event.data.attendance"].create(
                {
                    "event_id": self.event.id,
                    "registrant_id": self.individual.id,
                    "attendance_date": datetime.now(),
                }
            )

    def test_04_attendance_date_validation(self):
        """Test attendance date validation against event dates"""
        with self.assertRaises(ValidationError):
            self.env["spp.event.data.attendance"].create(
                {
                    "event_id": self.event.id,
                    "registrant_id": self.individual.id,
                    "attendance_date": datetime.now() + timedelta(days=5),  # Date outside event range
                }
            )
