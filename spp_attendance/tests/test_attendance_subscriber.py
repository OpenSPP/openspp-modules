from odoo.tests import TransactionCase


class TestAttendanceSubscriber(TransactionCase):
    def setUp(self):
        super().setUp()
        self.subscriber = self.env["spp.attendance.subscriber"].create(
            {
                "family_name": "Test",
                "given_name": "Subscriber",
                "person_identifier": "TEST123",
                "email": "test@example.com",
                "phone": "1234567890",
                "gender_char": "Male",
            }
        )

    def test_subscriber_creation(self):
        """Test subscriber creation and partner linking"""
        self.assertTrue(self.subscriber.partner_id)
        self.assertEqual(self.subscriber.name, "Test, Subscriber")
        self.assertEqual(self.subscriber.partner_id.name, "Test, Subscriber")
        self.assertEqual(self.subscriber.partner_id.identifier, "TEST123")

    def test_name_computation(self):
        """Test name computation from components"""
        self.assertEqual(self.subscriber.partner_name, "Test, Subscriber")

        self.subscriber.addl_name = "Middle"
        self.assertEqual(self.subscriber.partner_name, "Test, Subscriber Middle")

        self.subscriber.family_name = "NewTest"
        self.assertEqual(self.subscriber.partner_name, "NewTest, Subscriber Middle")

    def test_partner_sync(self):
        """Test synchronization with partner record"""
        self.subscriber.email = "newemail@example.com"
        self.assertEqual(self.subscriber.partner_id.email, "newemail@example.com")

        self.subscriber.phone = "0987654321"
        self.assertEqual(self.subscriber.partner_id.phone, "0987654321")

    def test_attendance_info(self):
        """Test attendance information retrieval"""
        # Create some attendance records
        self.env["spp.attendance.list"].create(
            [
                {
                    "subscriber_id": self.subscriber.id,
                    "attendance_date": "2024-03-20",
                    "attendance_time": "10:00:00",
                    "attendance_category": "present",
                    "submitted_by": "Test User",
                    "submitted_datetime": "2024-03-20 10:00:00",
                },
                {
                    "subscriber_id": self.subscriber.id,
                    "attendance_date": "2024-03-21",
                    "attendance_time": "10:00:00",
                    "attendance_category": "absent",
                    "submitted_by": "Test User",
                    "submitted_datetime": "2024-03-21 10:00:00",
                },
            ]
        )

        # Test attendance list retrieval
        total, info = self.subscriber.get_attendance_list()
        self.assertEqual(total, 2)
        self.assertEqual(info["person_id"], "TEST123")
        self.assertEqual(len(info["attendance_list"]), 2)
        self.assertEqual(len(info["dates_present"]), 1)  # Only one present attendance

        # Test subscriber info
        info = self.subscriber.get_attendance_subscriber_info()
        self.assertEqual(info["person_id"], "TEST123")
        self.assertEqual(info["name"], "Test, Subscriber")
        self.assertEqual(info["email"], "test@example.com") 