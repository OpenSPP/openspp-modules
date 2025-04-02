from unittest.mock import MagicMock, patch

from twilio.base.exceptions import TwilioRestException

from odoo.tests import TransactionCase

from odoo.addons.spp_sms.tools.sms_api import SmsApi


class TestSmsApi(TransactionCase):
    def setUp(self):
        super().setUp()
        # Create test IAP account for Twilio
        self.iap_account = self.env["iap.account"].create(
            {
                "service_name": "sms",
                "provider": "sms_twilio",
                "active_status": True,
                "sms_twilio_account_id": "test_account_id",
                "sms_twilio_token_id": "test_token",
                "sms_twilio_from": "+1234567890",
            }
        )

        self.sms_api = SmsApi(self.env)
        self.test_message = {
            "content": "Test SMS message",
            "numbers": [
                {"number": "+9876543210", "uuid": "test-uuid-1"},
                {"number": "+1122334455", "uuid": "test-uuid-2"},
            ],
        }

    @patch("odoo.addons.spp_sms.tools.sms_api.Client")
    def test_twilio_sms_success(self, mock_twilio_client):
        """Test successful SMS sending via Twilio"""
        # Create a mock instance
        mock_client_instance = MagicMock()
        mock_twilio_client.return_value = mock_client_instance

        # Mock the messages attribute and create method
        mock_messages = MagicMock()
        mock_client_instance.messages = mock_messages

        # Mock the response
        mock_message = MagicMock()
        mock_message.sid = "SM123"
        mock_messages.create.return_value = mock_message

        result = self.sms_api._send_sms_batch([self.test_message])

        # Verify results
        self.assertEqual(len(result), 2)
        for res in result:
            self.assertEqual(res["state"], "success")
            self.assertEqual(res["credit"], 0)

        # Verify Twilio was called with correct parameters
        mock_messages.create.assert_called_with(to="+1122334455", from_="+1234567890", body="Test SMS message")

    @patch("odoo.addons.spp_sms.tools.sms_api.Client")
    def test_twilio_sms_error(self, mock_twilio_client):
        """Test Twilio error handling"""
        # Mock Twilio error
        mock_twilio_client.return_value.messages.create.side_effect = TwilioRestException(
            uri="test", msg="Invalid number", code=21211, status=400
        )

        result = self.sms_api._send_sms_batch([self.test_message])

        # Verify error handling
        self.assertEqual(len(result), 2)
        for res in result:
            self.assertEqual(res["state"], "invalid_to_number")
            self.assertEqual(res["credit"], 0)

    def test_fallback_to_original_api(self):
        """Test fallback to original Odoo SMS API when Twilio is not configured"""
        # Deactivate Twilio account
        self.iap_account.active_status = False

        with patch("odoo.addons.sms.tools.sms_api.SmsApi._send_sms_batch") as mock_original:
            mock_original.return_value = [{"state": "success", "credit": 1}]

            result = self.sms_api._send_sms_batch([self.test_message])

            # Verify original API was called
            mock_original.assert_called_once()
            self.assertEqual(result, [{"state": "success", "credit": 1}])

    def test_sms_error_messages(self):
        """Test custom error messages for Twilio"""
        error_messages = self.sms_api._get_sms_api_error_messages()

        # Verify Twilio-specific error messages are present
        self.assertIn("invalid_to_number", error_messages)
        self.assertIn("invalid_from_number", error_messages)
        self.assertIn("cannot_be_reached", error_messages)
        self.assertIn("reached_rate_limit", error_messages)
        self.assertIn("invalid_from_number_mismatch", error_messages)
        self.assertIn("invalid_from_number_alphanumeric", error_messages)

        # Verify original error messages are still present
        self.assertIn("insufficient_credit", error_messages)
        self.assertIn("country_not_supported", error_messages)
