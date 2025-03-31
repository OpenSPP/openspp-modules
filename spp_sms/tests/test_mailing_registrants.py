# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from datetime import timedelta

from odoo.fields import Date
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestMailingRegistrants(TransactionCase):
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
                "is_registrant": True,
            }
        )

        cls.program = cls.env["g2p.program"].create(
            {
                "name": "Test Program",
            }
        )

        cls.cycle = cls.env["g2p.cycle"].create(
            {
                "name": "Test Cycle",
                "program_id": cls.program.id,
                "start_date": Date.today(),
                "end_date": Date.today() + timedelta(days=30),
            }
        )

        cls.mailing = cls.env["mailing.mailing"].create(
            {
                "name": "Test Mailing",
                "subject": "Test Subject",
                "mailing_type": "sms",
            }
        )

    def test_01_create_mailing_registrant(self):
        """Test creation of mailing registrant record"""
        mailing_registrant = self.env["spp.mailing.registrants"].create(
            {
                "registrant_id": self.registrant.id,
                "program_id": self.program.id,
                "cycle_id": self.cycle.id,
                "mailing_individual_id": self.mailing.id,
            }
        )

        self.assertEqual(mailing_registrant.registrant_id, self.registrant)
        self.assertEqual(mailing_registrant.program_id, self.program)
        self.assertEqual(mailing_registrant.cycle_id, self.cycle)
        self.assertEqual(mailing_registrant.mailing_individual_id, self.mailing)

    def test_02_multiple_mailing_types(self):
        """Test creating registrant with different mailing types"""
        mailing_registrant = self.env["spp.mailing.registrants"].create(
            {
                "registrant_id": self.registrant.id,
                "mailing_individual_id": self.mailing.id,
                "mailing_group_id": self.mailing.id,
                "mailing_program_id": self.mailing.id,
                "mailing_cycle_id": self.mailing.id,
            }
        )

        self.assertTrue(mailing_registrant.mailing_individual_id)
        self.assertTrue(mailing_registrant.mailing_group_id)
        self.assertTrue(mailing_registrant.mailing_program_id)
        self.assertTrue(mailing_registrant.mailing_cycle_id)

    def test_03_empty_optional_fields(self):
        """Test creating registrant with minimal required fields"""
        mailing_registrant = self.env["spp.mailing.registrants"].create(
            {
                "registrant_id": self.registrant.id,
                "mailing_individual_id": self.mailing.id,
            }
        )

        self.assertTrue(mailing_registrant.registrant_id)
        self.assertTrue(mailing_registrant.mailing_individual_id)
        self.assertFalse(mailing_registrant.program_id)
        self.assertFalse(mailing_registrant.cycle_id)
        self.assertFalse(mailing_registrant.mailing_group_id)
        self.assertFalse(mailing_registrant.mailing_program_id)
        self.assertFalse(mailing_registrant.mailing_cycle_id)
