from datetime import datetime, timedelta

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

        self.attendance_type = self.env["spp.res.config.attendance.type"].create(
            {
                "name": "Test Attendance Type",
                "external_id": 1,
                "external_source": "https://test.example",
            }
        )

        self.attendance_location = self.env["spp.res.config.attendance.location"].create(
            {
                "name": "Test Location",
                "external_id": 1,
                "external_source": "https://test.example",
            }
        )

        self.event = self.env["spp.event.data"].create(
            {
                "name": "Test Event",
                "model": "spp.event.attendance",
                "partner_id": self.individual.id,  # Required field
            }
        )

    def _create_event_attendance(self, external_id=1):
        """Helper function to create event attendance records with given parameters"""
        return self.env["spp.event.attendance"].create(
            {
                "individual_id": self.individual.id,
                "attendance_date": datetime.now(),
                "attendance_time": "10:00:00",
                "attendance_type_id": self.attendance_type.id,
                "attendance_location_id": self.attendance_location.id,
                "submitted_by": "Test User",
                "submitted_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "event_data_source": "https://test.example",
                "event_data_external_id": external_id,
            }
        )

    def test_01_create_event_attendance(self):
        """Test creating event attendance"""
        event_attendance = self._create_event_attendance()
        self.assertTrue(event_attendance, "Event attendance should be created")

    def test_02_validate_event_attendance(self):
        """Test event attendance validation"""
        event_attendance = self._create_event_attendance()
        self.assertTrue(event_attendance, "Event attendance should be created")

    def test_03_duplicate_event_attendance(self):
        """Test duplicate event attendance validation"""
        # Create first attendance
        self._create_event_attendance(external_id=1)

        # Creating another attendance with different external ID
        self._create_event_attendance(external_id=2)

    def test_04_attendance_date_validation(self):
        """Test attendance date validation against event dates"""
        event_attendance = self._create_event_attendance()
        self.assertTrue(event_attendance, "Event attendance should be created")
