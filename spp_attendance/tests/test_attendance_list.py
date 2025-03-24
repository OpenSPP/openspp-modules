from odoo.tests import TransactionCase


class TestAttendanceList(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create(
            {
                "name": "Test Partner",
                "family_name": "Test",
                "given_name": "Partner",
                "identifier": "TEST123",
            }
        )
        self.subscriber = self.env["spp.attendance.subscriber"].create(
            {
                "partner_id": self.partner.id,
                "person_identifier": "TEST123",
            }
        )
        self.type = self.env["spp.attendance.type"].create(
            {
                "name": "Test Type",
                "description": "Test Description",
            }
        )
        self.location = self.env["spp.attendance.location"].create(
            {
                "name": "Test Location",
                "description": "Test Description",
            }
        )

    def test_attendance_creation(self):
        """Test basic attendance creation"""
        attendance = self.env["spp.attendance.list"].create(
            {
                "subscriber_id": self.subscriber.id,
                "attendance_date": "2024-03-20",
                "attendance_time": "10:00:00",
                "attendance_type_id": self.type.id,
                "attendance_location_id": self.location.id,
                "attendance_description": "Test attendance",
                "attendance_category": "present",
                "submitted_by": "Test User",
                "submitted_datetime": "2024-03-20 10:00:00",
            }
        )

        self.assertEqual(attendance.subscriber_id, self.subscriber)
        self.assertEqual(attendance.attendance_date.strftime("%Y-%m-%d"), "2024-03-20")
        self.assertEqual(attendance.attendance_time, "10:00:00")
        self.assertEqual(attendance.attendance_type_id, self.type)
        self.assertEqual(attendance.attendance_location_id, self.location)
        self.assertEqual(attendance.attendance_category, "present")

    def test_attendance_uniqueness(self):
        """Test attendance uniqueness constraints"""
        # Enable all uniqueness constraints
        self.env["ir.config_parameter"].sudo().set_param("spp_attendance.date_unique", True)
        self.env["ir.config_parameter"].sudo().set_param("spp_attendance.time_unique", True)
        self.env["ir.config_parameter"].sudo().set_param("spp_attendance.type_unique", True)
        self.env["ir.config_parameter"].sudo().set_param("spp_attendance.location_unique", True)

        # Create first attendance
        attendance1 = self.env["spp.attendance.list"].create(
            {
                "subscriber_id": self.subscriber.id,
                "attendance_date": "2024-03-20",
                "attendance_time": "10:00:00",
                "attendance_type_id": self.type.id,
                "attendance_location_id": self.location.id,
                "attendance_category": "present",
                "submitted_by": "Test User",
                "submitted_datetime": "2024-03-20 10:00:00",
            }
        )

        # Try to create duplicate attendance
        attendance2 = self.env["spp.attendance.list"].new(
            {
                "subscriber_id": self.subscriber.id,
                "attendance_date": "2024-03-20",
                "attendance_time": "10:00:00",
                "attendance_type_id": self.type.id,
                "attendance_location_id": self.location.id,
                "attendance_category": "present",
                "submitted_by": "Test User",
                "submitted_datetime": "2024-03-20 10:00:00",
            }
        )

        self.assertFalse(attendance2.check_uniqueness())

        # Change time should allow creation
        attendance2.attendance_time = "11:00:00"
        self.assertTrue(attendance2.check_uniqueness())

    def test_attendance_categories(self):
        """Test attendance categories"""
        attendance = self.env["spp.attendance.list"].create(
            {
                "subscriber_id": self.subscriber.id,
                "attendance_date": "2024-03-20",
                "attendance_time": "10:00:00",
                "attendance_category": "present",
                "submitted_by": "Test User",
                "submitted_datetime": "2024-03-20 10:00:00",
            }
        )
        self.assertEqual(attendance.attendance_category, "present")

        attendance.attendance_category = "absent"
        self.assertEqual(attendance.attendance_category, "absent")
