# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestRegistrant(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set context to avoid job queue delay
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )

        # Create test data
        cls.registrant = cls.env["res.partner"].create(
            {
                "name": "Test Registrant",
                "is_group": False,
                "is_registrant": True,
            }
        )

        cls.mailing = cls.env["mailing.mailing"].create(
            {
                "name": "Test SMS Mailing",
                "subject": "Test",
                "mailing_type": "sms",
                "body_plaintext": "This is a test SMS",
            }
        )

    def test_01_mailing_sms_assignment(self):
        """Test assigning mailing SMS to registrant"""
        self.registrant.write({"mailing_sms_id": self.mailing.id})
        self.assertEqual(
            self.registrant.mailing_sms_id,
            self.mailing,
            "Mailing SMS should be correctly assigned to registrant",
        )

    def test_02_mailing_sms_unassignment(self):
        """Test removing mailing SMS from registrant"""
        # First assign
        self.registrant.write({"mailing_sms_id": self.mailing.id})
        # Then unassign
        self.registrant.write({"mailing_sms_id": False})
        self.assertFalse(
            self.registrant.mailing_sms_id,
            "Mailing SMS should be removed from registrant",
        )
