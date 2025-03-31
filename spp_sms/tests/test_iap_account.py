# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestIapAccount(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set up test environment
        cls.env = cls.env(context=dict(cls.env.context, test_queue_job_no_delay=True))

        # Create test IAP accounts
        cls.iap_odoo = cls.env["iap.account"].create(
            {
                "name": "Test Odoo IAP",
                "provider": "odoo",
                "active_status": True,
            }
        )

        cls.iap_twilio = cls.env["iap.account"].create(
            {
                "name": "Test Twilio",
                "provider": "sms_twilio",
                "sms_twilio_account_id": "test_account_id",
                "sms_twilio_token_id": "test_token_id",
                "sms_twilio_from": "+1234567890",
                "active_status": True,
            }
        )

        cls.iap_sns = cls.env["iap.account"].create(
            {
                "name": "Test Amazon SNS",
                "provider": "sns_amazon",
                "sns_amazon_key": "test_key",
                "sns_amazon_secret": "test_secret",
                "sns_amazon_region": "us-east-1",
                "active_status": True,
            }
        )

    def test_01_create_iap_account(self):
        """Test IAP account creation with different providers"""
        # Test Odoo IAP
        self.assertEqual(self.iap_odoo.provider, "odoo")
        self.assertTrue(self.iap_odoo.active_status)

        # Test Twilio
        self.assertEqual(self.iap_twilio.provider, "sms_twilio")
        self.assertEqual(self.iap_twilio.sms_twilio_account_id, "test_account_id")
        self.assertEqual(self.iap_twilio.sms_twilio_token_id, "test_token_id")
        self.assertEqual(self.iap_twilio.sms_twilio_from, "+1234567890")
        self.assertTrue(self.iap_twilio.active_status)

        # Test Amazon SNS
        self.assertEqual(self.iap_sns.provider, "sns_amazon")
        self.assertEqual(self.iap_sns.sns_amazon_key, "test_key")
        self.assertEqual(self.iap_sns.sns_amazon_secret, "test_secret")
        self.assertEqual(self.iap_sns.sns_amazon_region, "us-east-1")
        self.assertTrue(self.iap_sns.active_status)

    def test_02_update_iap_account(self):
        """Test updating IAP account fields"""
        # Update Twilio account
        self.iap_twilio.write(
            {
                "sms_twilio_account_id": "new_account_id",
                "sms_twilio_from": "+9876543210",
                "active_status": False,
            }
        )
        self.assertEqual(self.iap_twilio.sms_twilio_account_id, "new_account_id")
        self.assertEqual(self.iap_twilio.sms_twilio_from, "+9876543210")
        self.assertFalse(self.iap_twilio.active_status)

        # Update Amazon SNS account
        self.iap_sns.write(
            {
                "sns_amazon_region": "eu-west-1",
                "active_status": False,
            }
        )
        self.assertEqual(self.iap_sns.sns_amazon_region, "eu-west-1")
        self.assertFalse(self.iap_sns.active_status)
