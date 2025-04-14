# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from datetime import timedelta

from odoo.fields import Date
from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tools.safe_eval import safe_eval


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

        cls.mailing = cls.env["mailing.mailing"].create(
            {
                "name": "Test Mailing",
                "subject": "Test",
                "mailing_type": "sms",
                "mailing_registrant_type": "Individual",
                "mailing_domain": "[('id', '=', 1)]",  # Set an initial domain
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
        actual_ids = safe_eval(mailing.mailing_domain)[0][2]
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
        actual_ids = safe_eval(mailing.mailing_domain)[0][2]
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
        actual_ids = safe_eval(mailing.mailing_domain)[0][2]
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
                "mailing_domain": "[('id', '=', 1)]",  # Set initial domain explicitly
            }
        )

        # Initially should have domain targeting SuperUser
        actual_ids = []
        if mailing.mailing_domain:
            domain = safe_eval(mailing.mailing_domain)
            if domain and len(domain) > 0:
                # Handle both single value and list cases
                value = domain[0][2]
                actual_ids = [value] if isinstance(value, int) else value
        self.assertEqual(actual_ids, [1])

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
        domain = safe_eval(mailing.mailing_domain)[0][2]
        actual_ids = [domain] if isinstance(domain, int) else domain
        expected_ids = [self.individual_1.id]

        # Sort both lists before comparison
        self.assertEqual(sorted(actual_ids), sorted(expected_ids))

    def test_06_update_mailing_domain_empty_vals(self):
        """Test that _update_mailing_domain handles empty vals correctly"""

        # Call method with empty list
        self.mailing._update_mailing_domain([])

        # Verify domain wasn't changed
        self.assertEqual(
            self.mailing.mailing_domain,
            "[]",
            "Domain should not change when vals is empty",
        )

        # Call method with None
        self.mailing._update_mailing_domain(None)

        # Verify domain wasn't changed
        self.assertEqual(
            self.mailing.mailing_domain,
            "[]",
            "Domain should not change when vals is None",
        )

    def test_07_non_sms_mailing_type(self):
        """Test that registrant type changes don't affect non-SMS mailings"""
        # Create a non-SMS mailing (e.g. email)
        mailing = self.env["mailing.mailing"].create(
            {
                "subject": "Test Subject",
                "name": "Test Email Mailing",
                "mailing_type": "mail",  # Not SMS
                "mailing_registrant_type": "Individual",
                "body_html": "<p>Test Email</p>",
            }
        )

        # Set an initial domain to verify it doesn't change
        initial_domain = "[('id', '=', 1)]"
        mailing.mailing_domain = initial_domain

        # Add registrants and trigger onchange - should not affect domain
        mailing.write(
            {
                "mailing_registrant_individual_ids": [
                    (0, 0, {"registrant_id": self.individual_1.id}),
                ],
            }
        )
        mailing._registrant_type_onchange()
        self.assertEqual(
            mailing.mailing_domain,
            initial_domain,
            "Domain should not change for non-SMS mailings",
        )

        # Change registrant type - should not affect domain
        mailing.mailing_registrant_type = "Group"
        mailing._registrant_type_onchange()
        self.assertEqual(
            mailing.mailing_domain,
            initial_domain,
            "Domain should not change when changing registrant type for non-SMS mailings",
        )

    def test_08_registrant_type_comprehensive(self):
        """Test all registrant type cases and transitions comprehensively"""
        mailing = self.env["mailing.mailing"].create(
            {
                "subject": "Test Subject",
                "name": "Test Comprehensive",
                "mailing_type": "sms",
                "mailing_registrant_type": "Individual",
                "body_plaintext": "Test SMS",
            }
        )

        # Test 1: Individual type
        mailing.write(
            {
                "mailing_registrant_individual_ids": [
                    (0, 0, {"registrant_id": self.individual_1.id}),
                    (0, 0, {"registrant_id": self.individual_2.id}),
                ],
            }
        )
        mailing._registrant_type_onchange()
        actual_ids = safe_eval(mailing.mailing_domain)[0][2]
        expected_ids = [self.individual_1.id, self.individual_2.id]
        self.assertEqual(sorted(actual_ids), sorted(expected_ids), "Individual type domain incorrect")

        # Test 2: Group type
        mailing.mailing_registrant_type = "Group"
        mailing.write(
            {
                "mailing_registrant_group_ids": [
                    (0, 0, {"registrant_id": self.group.id}),
                ],
            }
        )
        mailing._registrant_type_onchange()
        actual_ids = safe_eval(mailing.mailing_domain)[0][2]
        expected_ids = [self.individual_1.id, self.individual_2.id]
        self.assertEqual(sorted(actual_ids), sorted(expected_ids), "Group type domain incorrect")

        # Test 3: Program type with enrolled members
        mailing.mailing_registrant_type = "Program"
        mailing.write(
            {
                "mailing_program_ids": [
                    (0, 0, {"program_id": self.program.id}),
                ],
            }
        )
        mailing._program_ids_onchange()
        actual_ids = safe_eval(mailing.mailing_domain)[0][2]
        expected_ids = [self.individual_1.id, self.individual_2.id]
        self.assertEqual(sorted(actual_ids), sorted(expected_ids), "Program type domain incorrect")

        # Test 4: Cycle type
        mailing.mailing_registrant_type = "Cycle"
        mailing.write(
            {
                "mailing_cycle_ids": [
                    (0, 0, {"cycle_id": self.cycle.id}),
                ],
            }
        )
        mailing._cycle_ids_onchange()
        actual_ids = safe_eval(mailing.mailing_domain)[0][2]
        expected_ids = [self.individual_1.id, self.individual_2.id]
        self.assertEqual(sorted(actual_ids), sorted(expected_ids), "Cycle type domain incorrect")

        # Test 5: Non-SMS type (should not modify domain)
        mailing = self.env["mailing.mailing"].create(
            {
                "subject": "Test Subject",
                "name": "Test Email Mailing",
                "mailing_type": "mail",
                "mailing_registrant_type": "Individual",
                "body_html": "<p>Test Email</p>",
            }
        )

        # Set initial domain for mail type
        mailing.mailing_domain = "[('list_ids', 'in', [])]"
        initial_domain = mailing.mailing_domain

        # Add registrants and change type - domain should not change
        mailing.write(
            {
                "mailing_registrant_individual_ids": [
                    (0, 0, {"registrant_id": self.individual_1.id}),
                ],
            }
        )
        mailing._registrant_type_onchange()
        self.assertEqual(
            mailing.mailing_domain,
            initial_domain,
            "Non-SMS type should not change domain",
        )

        # Test 6: Empty records for each type
        mailing = self.env["mailing.mailing"].create(
            {
                "subject": "Test Subject",
                "name": "Test Empty Records",
                "mailing_type": "sms",
                "mailing_registrant_type": "Individual",
                "body_plaintext": "Test SMS",
            }
        )

        # Test each type with empty records
        for reg_type in ["Individual", "Group", "Program", "Cycle"]:
            mailing.mailing_registrant_type = reg_type
            mailing._registrant_type_onchange()
            self.assertEqual(
                mailing.mailing_domain,
                "[]",
                f"Empty {reg_type} type should have empty domain",
            )

        # Test 7: Multiple programs with enrolled and non-enrolled members
        mailing.mailing_registrant_type = "Program"
        # Create a new program with non-enrolled membership
        new_program = self.env["g2p.program"].create(
            {
                "name": "Test Program 2",
            }
        )
        self.env["g2p.program_membership"].create(
            {
                "partner_id": self.group.id,
                "program_id": new_program.id,
                "state": "draft",  # Non-enrolled state
            }
        )

        mailing.write(
            {
                "mailing_program_ids": [
                    (0, 0, {"program_id": self.program.id}),
                    (0, 0, {"program_id": new_program.id}),
                ],
            }
        )
        mailing._program_ids_onchange()
        actual_ids = safe_eval(mailing.mailing_domain)[0][2]
        expected_ids = [
            self.individual_1.id,
            self.individual_2.id,
        ]  # Only enrolled members
        self.assertEqual(
            sorted(actual_ids),
            sorted(expected_ids),
            "Program type should only include enrolled members",
        )

    def test_09_individual_program_membership(self):
        """Test SMS mailing for programs with individual (non-group) members"""
        # Create program membership for an individual
        self.env["g2p.program_membership"].create(
            {
                "partner_id": self.individual_1.id,  # Direct individual membership
                "program_id": self.program.id,
                "state": "enrolled",
            }
        )

        # Create mailing targeting the program
        mailing = self.env["mailing.mailing"].create(
            {
                "subject": "Test Subject",
                "name": "Test Individual Program Member",
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

        # Get actual domain and verify it includes the individual
        actual_ids = safe_eval(mailing.mailing_domain)[0][2]
        expected_ids = [
            self.individual_1.id,  # Individual member
            self.individual_1.id,  # From group membership
            self.individual_2.id,  # From group membership
        ]

        # Sort and remove duplicates before comparison since individual_1 appears twice
        self.assertEqual(
            sorted(list(set(actual_ids))),
            sorted(list(set(expected_ids))),
            "Domain should include both individual and group members",
        )

    def test_10_program_type_onchange(self):
        """Test program type onchange with multiple programs and member states"""
        # Create additional test data
        individual_3 = self.env["res.partner"].create(
            {
                "name": "Test Individual 3",
                "is_group": False,
                "is_registrant": True,
                "phone": "+1234567892",
            }
        )

        # Create a new program with mixed membership states
        program_2 = self.env["g2p.program"].create(
            {
                "name": "Test Program 2",
            }
        )

        # Create memberships with different states
        memberships = [
            # Enrolled individual
            {
                "partner_id": individual_3.id,
                "program_id": self.program.id,
                "state": "enrolled",
            },
            # Draft state - should not be included
            {
                "partner_id": self.individual_2.id,
                "program_id": program_2.id,
                "state": "draft",
            },
            # Enrolled group
            {
                "partner_id": self.group.id,
                "program_id": program_2.id,
                "state": "enrolled",
            },
        ]

        for membership in memberships:
            self.env["g2p.program_membership"].create(membership)

        # Create mailing targeting both programs
        mailing = self.env["mailing.mailing"].create(
            {
                "subject": "Test Subject",
                "name": "Test Program Type Onchange",
                "mailing_type": "sms",
                "mailing_registrant_type": "Program",
                "body_plaintext": "Test SMS",
                "mailing_program_ids": [
                    (0, 0, {"program_id": self.program.id}),
                    (0, 0, {"program_id": program_2.id}),
                ],
            }
        )

        # Trigger program_ids onchange instead of registrant_type_onchange
        # This is the correct method to test since it properly handles the program records
        mailing._program_ids_onchange()

        # Get actual domain and verify it includes only enrolled members
        actual_ids = safe_eval(mailing.mailing_domain)[0][2]
        expected_ids = [
            individual_3.id,  # Enrolled individual in program 1
            self.individual_1.id,  # From enrolled group in program 2
            self.individual_2.id,  # From enrolled group in program 2
        ]

        # Sort and remove duplicates before comparison
        self.assertEqual(
            sorted(list(set(actual_ids))),
            sorted(list(set(expected_ids))),
            "Domain should only include enrolled members from both programs",
        )

        # Test changing registrant type clears domain
        mailing.mailing_registrant_type = "Individual"
        mailing._registrant_type_onchange()
        self.assertEqual(
            mailing.mailing_domain,
            "[]",
            "Domain should be cleared when changing registrant type",
        )
