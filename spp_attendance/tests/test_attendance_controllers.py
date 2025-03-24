import json
from datetime import datetime
from unittest.mock import patch

from odoo.tests import HttpCase, tagged


@tagged("-at_install", "post_install")
class TestAttendanceControllers(HttpCase):
    def setUp(self):
        super().setUp()
        self.client = self.env["spp.attendance.api.client.credential"].create({"name": "Test Client"})
        self.type = self.env["spp.attendance.type"].create({"name": "Test Type"})
        self.location = self.env["spp.attendance.location"].create({"name": "Test Location"})

    @patch("jwt.encode")
    @patch("odoo.addons.spp_oauth.tools.rsa_encode_decode.get_private_key")
    def test_auth_token(self, mock_get_private_key, mock_jwt_encode):
        """Test authentication token endpoint"""
        mock_get_private_key.return_value = "test_private_key"
        mock_jwt_encode.return_value = "test_token"
        data = {
            "client_id": self.client.client_id,
            "client_secret": self.client.client_secret,
        }
        response = self.url_open(
            "/auth/token",
            data=json.dumps(data),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result.get("access_token"), "test_token")
        self.assertEqual(result.get("token_type"), "Bearer")

    @patch("jwt.encode")
    @patch("odoo.addons.spp_oauth.tools.rsa_encode_decode.get_private_key")
    @patch("odoo.addons.spp_oauth.tools.rsa_encode_decode.get_public_key")
    @patch("jwt.decode")
    def test_create_attendance(self, mock_jwt_decode, mock_get_public_key, mock_get_private_key, mock_jwt_encode):
        """Test attendance creation endpoint"""
        mock_get_private_key.return_value = "test_private_key"
        mock_get_public_key.return_value = "test_public_key"
        mock_jwt_encode.return_value = "test_token"
        mock_jwt_decode.return_value = {"iss": "openspp:auth-service"}

        # First get auth token
        auth_data = {
            "client_id": self.client.client_id,
            "client_secret": self.client.client_secret,
        }
        auth_response = self.url_open(
            "/auth/token",
            data=json.dumps(auth_data),
            headers={"Content-Type": "application/json"},
        )
        token = json.loads(auth_response.content)["access_token"]

        # Create attendance
        attendance_data = {
            "records": [
                {
                    "person_id": "TEST123",
                    "time_card": [
                        {
                            "date_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "attendance_type": self.type.id,
                            "attendance_location": self.location.id,
                            "attendance_category": "present",
                        }
                    ],
                }
            ],
            "submitted_by": "Test User",
            "submitted_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        response = self.url_open(
            "/attendances",
            data=json.dumps(attendance_data),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
        )

        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result["message"], "Attendance list created successfully.")
        self.assertEqual(result["person_ids"], ["TEST123"])

    @patch("jwt.encode")
    @patch("odoo.addons.spp_oauth.tools.rsa_encode_decode.get_private_key")
    @patch("odoo.addons.spp_oauth.tools.rsa_encode_decode.get_public_key")
    @patch("jwt.decode")
    def test_get_attendance(self, mock_jwt_decode, mock_get_public_key, mock_get_private_key, mock_jwt_encode):
        """Test attendance retrieval endpoint"""
        mock_get_private_key.return_value = "test_private_key"
        mock_get_public_key.return_value = "test_public_key"
        mock_jwt_encode.return_value = "test_token"
        mock_jwt_decode.return_value = {"iss": "openspp:auth-service"}

        # Setup auth and create some attendance records first
        auth_data = {
            "client_id": self.client.client_id,
            "client_secret": self.client.client_secret,
        }
        auth_response = self.url_open(
            "/auth/token",
            data=json.dumps(auth_data),
            headers={"Content-Type": "application/json"},
        )
        token = json.loads(auth_response.content)["access_token"]

        subscriber = self.env["spp.attendance.subscriber"].create(
            {
                "family_name": "Test",
                "given_name": "Subscriber",
                "person_identifier": "TEST123",
            }
        )

        self.env["spp.attendance.list"].create(
            {
                "subscriber_id": subscriber.id,
                "attendance_date": datetime.now().strftime("%Y-%m-%d"),
                "attendance_time": "10:00:00",
                "attendance_type_id": self.type.id,
                "attendance_location_id": self.location.id,
                "attendance_category": "present",
                "submitted_by": "Test User",
                "submitted_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

        # Test get attendance
        response = self.url_open(
            f"/attendance/{subscriber.person_identifier}",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
        )

        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result["person_id"], "TEST123")
        self.assertEqual(len(result["attendance_list"]), 1)
