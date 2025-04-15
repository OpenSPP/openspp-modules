from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestAttendanceConfig(TransactionCase):
    def setUp(self):
        super().setUp()

    def test_01_create_attendance_type(self):
        """Test creating attendance type"""
        attendance_type = self.env["g2p.attendance.type"].create(
            {
                "name": "Test Type",
                "code": "TEST",
                "description": "Test Description",
            }
        )

        self.assertTrue(attendance_type, "Attendance type should be created")
        self.assertEqual(attendance_type.code, "TEST", "Code should match")

    def test_02_duplicate_attendance_type_code(self):
        """Test duplicate attendance type code validation"""
        self.env["g2p.attendance.type"].create(
            {
                "name": "Test Type 1",
                "code": "TEST",
            }
        )

        with self.assertRaises(ValidationError):
            self.env["g2p.attendance.type"].create(
                {
                    "name": "Test Type 2",
                    "code": "TEST",  # Duplicate code
                }
            )

    def test_03_create_attendance_location(self):
        """Test creating attendance location"""
        location = self.env["g2p.attendance.location"].create(
            {
                "name": "Test Location",
                "code": "LOC1",
                "description": "Test Location Description",
            }
        )

        self.assertTrue(location, "Attendance location should be created")
        self.assertEqual(location.code, "LOC1", "Code should match")

    def test_04_duplicate_location_code(self):
        """Test duplicate location code validation"""
        self.env["g2p.attendance.location"].create(
            {
                "name": "Test Location 1",
                "code": "LOC1",
            }
        )

        with self.assertRaises(ValidationError):
            self.env["g2p.attendance.location"].create(
                {
                    "name": "Test Location 2",
                    "code": "LOC1",  # Duplicate code
                }
            )
