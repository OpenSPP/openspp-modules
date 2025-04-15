from datetime import datetime, timedelta

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestCycleAttendance(TransactionCase):
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

        self.attendance_type = self.env["g2p.attendance.type"].create(
            {
                "name": "Test Attendance Type",
                "code": "TEST",
            }
        )

        self.attendance_location = self.env["g2p.attendance.location"].create(
            {
                "name": "Test Location",
                "code": "LOC1",
            }
        )

        self.individual = self.env["res.partner"].create(
            {
                "name": "Test Individual",
                "is_registrant": True,
            }
        )

    def test_01_create_cycle_attendance(self):
        """Test creating cycle attendance"""
        attendance = self.env["g2p.cycle.membership.attendance"].create(
            {
                "cycle_id": self.cycle.id,
                "attendance_type_id": self.attendance_type.id,
                "attendance_location_id": self.attendance_location.id,
                "registrant_id": self.individual.id,
                "attendance_date": datetime.now(),
            }
        )

        self.assertTrue(attendance, "Attendance should be created")
        self.assertEqual(attendance.state, "draft", "Initial state should be draft")

    def test_02_validate_attendance(self):
        """Test attendance validation"""
        attendance = self.env["g2p.cycle.membership.attendance"].create(
            {
                "cycle_id": self.cycle.id,
                "attendance_type_id": self.attendance_type.id,
                "attendance_location_id": self.attendance_location.id,
                "registrant_id": self.individual.id,
                "attendance_date": datetime.now(),
            }
        )

        attendance.action_validate()
        self.assertEqual(attendance.state, "validated", "State should be validated after validation")

    def test_03_duplicate_attendance(self):
        """Test duplicate attendance validation"""
        self.env["g2p.cycle.membership.attendance"].create(
            {
                "cycle_id": self.cycle.id,
                "attendance_type_id": self.attendance_type.id,
                "attendance_location_id": self.attendance_location.id,
                "registrant_id": self.individual.id,
                "attendance_date": datetime.now(),
            }
        )

        with self.assertRaises(ValidationError):
            self.env["g2p.cycle.membership.attendance"].create(
                {
                    "cycle_id": self.cycle.id,
                    "attendance_type_id": self.attendance_type.id,
                    "attendance_location_id": self.attendance_location.id,
                    "registrant_id": self.individual.id,
                    "attendance_date": datetime.now(),
                }
            )

    def test_04_attendance_date_validation(self):
        """Test attendance date validation"""
        with self.assertRaises(ValidationError):
            self.env["g2p.cycle.membership.attendance"].create(
                {
                    "cycle_id": self.cycle.id,
                    "attendance_type_id": self.attendance_type.id,
                    "attendance_location_id": self.attendance_location.id,
                    "registrant_id": self.individual.id,
                    "attendance_date": datetime.now() + timedelta(days=60),  # Date outside cycle range
                }
            )
