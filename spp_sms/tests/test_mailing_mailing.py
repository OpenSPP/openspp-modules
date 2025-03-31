from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.fields import Date
from datetime import timedelta


@tagged("post_install", "-at_install")
class TestMailingMailing(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create test individuals
        cls.individual_1 = cls.env["res.partner"].create(
            {
                "name": "Test Individual 1",
                "is_group": False,
                "is_registrant": True,
                "phone": "+1234567890",
            }
        )
        cls.individual_2 = cls.env["res.partner"].create(
            {
                "name": "Test Individual 2",
                "is_group": False,
                "is_registrant": True,
                "phone": "+1234567891",
            }
        )

        # Create test group
        cls.group = cls.env["res.partner"].create(
            {
                "name": "Test Group",
                "is_group": True,
                "is_registrant": True,
            }
        )

        # Add individuals to group
        members = [
            {"individual": cls.individual_1.id},
            {"individual": cls.individual_2.id},
        ]
        group_members = [[0, 0, val] for val in members]
        cls.group.write({"group_membership_ids": group_members})

        # Create test program
        cls.program = cls.env["g2p.program"].create(
            {
                "name": "Test Program",
            }
        )

        # Create program membership
        cls.program_membership = cls.env["g2p.program_membership"].create(
            {
                "partner_id": cls.group.id,
                "program_id": cls.program.id,
                "state": "enrolled",
            }
        )

        # Create test cycle
        cls.cycle = cls.env["g2p.cycle"].create(
            {
                "name": "Test Cycle",
                "program_id": cls.program.id,
                "start_date": Date.today(),
                "end_date": Date.today() + timedelta(days=30),
            }
        )

        # Create cycle membership
        cls.cycle_membership = cls.env["g2p.cycle.membership"].create(
            {
                "partner_id": cls.group.id,
                "cycle_id": cls.cycle.id,
                "state": "enrolled",
            }
        )

    def test_01_individual_mailing(self):
        """Test SMS mailing for individual registrants"""
        mailing = self.env["mailing.mailing"].create(
            {
                "subject": "Test Subject",
                "name": "Test Individual Mailing",
                "mailing_type": "sms",
                "mailing_registrant_type": "Individual",
                "body_plaintext": "Test SMS",
                "mailing_registrant_individual_ids": [
                    (0, 0, {"registrant_id": self.individual_1.id}),
                ],
            }
        )

        # Trigger onchange
        mailing._individual_ids_onchange()

        expected_domain = f"[('id', 'in', [{self.individual_1.id}])]"
        self.assertEqual(mailing.mailing_domain, expected_domain)

    def test_02_group_mailing(self):
        """Test SMS mailing for group registrants"""
        mailing = self.env["mailing.mailing"].create(
            {
                "subject": "Test Subject",
                "name": "Test Group Mailing",
                "mailing_type": "sms",
                "mailing_registrant_type": "Group",
                "body_plaintext": "Test SMS",
                "mailing_registrant_group_ids": [
                    (0, 0, {"registrant_id": self.group.id}),
                ],
            }
        )

        # Trigger onchange
        mailing._group_ids_onchange()

        # Get actual domain and expected domain as lists of IDs
        actual_ids = eval(mailing.mailing_domain)[0][2]
        expected_ids = [self.individual_1.id, self.individual_2.id]

        # Sort both lists before comparison
        self.assertEqual(sorted(actual_ids), sorted(expected_ids))

    def test_03_program_mailing(self):
        """Test SMS mailing for program registrants"""
        mailing = self.env["mailing.mailing"].create(
            {
                "subject": "Test Subject",
                "name": "Test Program Mailing",
                "mailing_type": "sms",
                "mailing_registrant_type": "Program",
                "body_plaintext": "Test SMS",
                "mailing_program_ids": [
                    (0, 0, {"program_id": self.program.id}),
                ],
            }
        )

        # Trigger onchange
        mailing._program_ids_onchange()

        # Get actual domain and expected domain as lists of IDs
        actual_ids = eval(mailing.mailing_domain)[0][2]
        expected_ids = [self.individual_1.id, self.individual_2.id]

        # Sort both lists before comparison
        self.assertEqual(sorted(actual_ids), sorted(expected_ids))

    def test_04_cycle_mailing(self):
        """Test SMS mailing for cycle registrants"""
        mailing = self.env["mailing.mailing"].create(
            {
                "subject": "Test Subject",
                "name": "Test Cycle Mailing",
                "mailing_type": "sms",
                "mailing_registrant_type": "Cycle",
                "body_plaintext": "Test SMS",
                "mailing_cycle_ids": [
                    (0, 0, {"cycle_id": self.cycle.id}),
                ],
            }
        )

        # Trigger onchange
        mailing._cycle_ids_onchange()

        # Get actual domain and expected domain as lists of IDs
        actual_ids = eval(mailing.mailing_domain)[0][2]
        expected_ids = [self.individual_1.id, self.individual_2.id]

        # Sort both lists before comparison
        self.assertEqual(sorted(actual_ids), sorted(expected_ids))


def test_05_registrant_type_change(self):
    """Test mailing domain updates when registrant type changes"""
    mailing = self.env["mailing.mailing"].create(
        {
            "subject": "Test Subject",
            "name": "Test Type Change Mailing",
            "mailing_type": "sms",
            "mailing_registrant_type": "Individual",
            "body_plaintext": "Test SMS",
        }
    )

    # Initially should have no target recipients
    actual_ids = []
    if mailing.mailing_domain:
        domain = eval(mailing.mailing_domain)
        if domain and len(domain) > 0 and len(domain[0]) > 2:
            actual_ids = domain[0][2]
    self.assertEqual(actual_ids, [])

    # Add individual and check domain
    mailing.write(
        {
            "mailing_registrant_individual_ids": [
                (0, 0, {"registrant_id": self.individual_1.id}),
            ],
        }
    )
    mailing._registrant_type_onchange()

    # Get actual domain and expected domain as lists of IDs
    actual_ids = eval(mailing.mailing_domain)[0][2]
    expected_ids = [self.individual_1.id]

    # Sort both lists before comparison
    self.assertEqual(sorted(actual_ids), sorted(expected_ids))
