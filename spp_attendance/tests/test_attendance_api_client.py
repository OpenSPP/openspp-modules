from datetime import datetime, timedelta
from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestAttendanceApiClient(TransactionCase):
    def setUp(self):
        super().setUp()
        self.client = self.env["spp.attendance.api.client.credential"].create({"name": "Test Client"})

    def test_generate_client_id(self):
        """Test client ID generation is unique and follows format"""
        client_id = self.client.client_id
        self.assertTrue(client_id.startswith("c-id-"))
        self.assertEqual(len(client_id), 41)  # c-id- + 36 chars UUID

        # Test uniqueness
        client2 = self.env["spp.attendance.api.client.credential"].create({"name": "Test Client 2"})
        self.assertNotEqual(client_id, client2.client_id)

    def test_generate_client_secret(self):
        """Test client secret generation is unique and follows format"""
        client_secret = self.client.client_secret
        self.assertTrue(client_secret.startswith("c-secret-"))
        self.assertEqual(len(client_secret), 45)  # c-secret- + 36 chars UUID

        # Test uniqueness
        client2 = self.env["spp.attendance.api.client.credential"].create({"name": "Test Client 2"})
        self.assertNotEqual(client_secret, client2.client_secret)

    @patch("jwt.encode")
    @patch("odoo.addons.spp_oauth.tools.rsa_encode_decode.get_private_key")
    def test_generate_access_token(self, mock_get_private_key, mock_jwt_encode):
        """Test access token generation"""
        mock_get_private_key.return_value = "test_private_key"
        mock_jwt_encode.return_value = "test_token"
        token = self.client.generate_access_token()
        self.assertEqual(token, "test_token")
        self.assertTrue(mock_jwt_encode.called)

    def test_show_credentials(self):
        """Test showing credentials works only once"""
        # First time should work
        action = self.client.show_credentials()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertTrue(self.client.show_button_clicked)

        # Second time should raise error
        with self.assertRaises(UserError):
            self.client.show_credentials()

    def test_export_data_restriction(self):
        """Test export data is restricted"""
        with self.assertRaises(UserError):
            self.client.export_data(["name", "client_id"])

    @patch("jwt.encode")
    @patch("odoo.addons.spp_oauth.tools.rsa_encode_decode.get_private_key")
    @patch("odoo.addons.spp_attendance.models.attendance_api_client_credentials.TOKEN_EXPIRATION_MIN", 10)
    def test_token_expiration(self, mock_get_private_key, mock_jwt_encode):
        """Test token expiration time"""
        mock_get_private_key.return_value = "test_private_key"
        mock_jwt_encode.side_effect = ["token1", "token2"]
        now = datetime.now()
        with patch("odoo.addons.spp_attendance.models.attendance_api_client_credentials.datetime") as mock_datetime:
            mock_datetime.today.return_value = now
            mock_datetime.strptime = datetime.strptime
            mock_datetime.now.return_value = now

            token = self.client.generate_access_token()
            self.assertEqual(token, "token1")

            # Token should be valid for TOKEN_EXPIRATION_MIN minutes
            mock_datetime.today.return_value = now + timedelta(minutes=9)
            token2 = self.client.generate_access_token()
            self.assertEqual(token2, "token2")
