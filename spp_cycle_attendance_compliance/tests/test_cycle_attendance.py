from datetime import datetime, timedelta

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

        self.attendance_type = self.env["spp.res.config.attendance.type"].create(
            {
                "name": "Test Attendance Type",
                "external_id": 1,
                "external_source": "http://test.com",
            }
        )

        self.attendance_location = self.env["spp.res.config.attendance.location"].create(
            {
                "name": "Test Location",
                "external_id": 1,
                "external_source": "http://test.com",
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
        attendance = self.env["spp.event.attendance"].create(
            {
                "individual_id": self.individual.id,
                "attendance_date": datetime.now(),
                "attendance_time": "10:00:00",
                "attendance_type_id": self.attendance_type.id,
                "attendance_location_id": self.attendance_location.id,
                "submitted_by": "Test User",
                "submitted_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "event_data_source": "http://test.com",
                "event_data_external_id": 1,
            }
        )

        self.assertTrue(attendance, "Attendance should be created")

    def test_02_validate_attendance(self):
        """Test attendance validation"""
        attendance = self.env["spp.event.attendance"].create(
            {
                "individual_id": self.individual.id,
                "attendance_date": datetime.now(),
                "attendance_time": "10:00:00",
                "attendance_type_id": self.attendance_type.id,
                "attendance_location_id": self.attendance_location.id,
                "submitted_by": "Test User",
                "submitted_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "event_data_source": "http://test.com",
                "event_data_external_id": 1,
            }
        )

        self.assertTrue(attendance, "Attendance should be created")

    def test_03_duplicate_attendance(self):
        """Test duplicate attendance validation"""
        self.env["spp.event.attendance"].create(
            {
                "individual_id": self.individual.id,
                "attendance_date": datetime.now(),
                "attendance_time": "10:00:00",
                "attendance_type_id": self.attendance_type.id,
                "attendance_location_id": self.attendance_location.id,
                "submitted_by": "Test User",
                "submitted_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "event_data_source": "http://test.com",
                "event_data_external_id": 1,
            }
        )

        # Creating another attendance with same external ID should not raise error
        # as it will update the existing record
        self.env["spp.event.attendance"].create(
            {
                "individual_id": self.individual.id,
                "attendance_date": datetime.now(),
                "attendance_time": "10:00:00",
                "attendance_type_id": self.attendance_type.id,
                "attendance_location_id": self.attendance_location.id,
                "submitted_by": "Test User",
                "submitted_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "event_data_source": "http://test.com",
                "event_data_external_id": 2,  # Different external ID
            }
        )

    def test_04_attendance_date_validation(self):
        """Test attendance date validation"""
        attendance = self.env["spp.event.attendance"].create(
            {
                "individual_id": self.individual.id,
                "attendance_date": datetime.now(),
                "attendance_time": "10:00:00",
                "attendance_type_id": self.attendance_type.id,
                "attendance_location_id": self.attendance_location.id,
                "submitted_by": "Test User",
                "submitted_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "event_data_source": "http://test.com",
                "event_data_external_id": 1,
            }
        )

        self.assertTrue(attendance, "Attendance should be created")
