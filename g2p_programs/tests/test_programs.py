import logging

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class ProgramTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        _logger.info("Program Testing: SETUP INITIALIZED")
        super(ProgramTest, cls).setUpClass()

        # Initial Setup of Variables
        cls.registrant_1 = cls.env["res.partner"].create(
            {
                "family_name": "Doe",
                "given_name": "John",
                "name": "John Doe",
                "is_group": False,
            }
        )
        cls.group_1 = cls.env["res.partner"].create(
            {
                "name": "Group 1",
                "is_group": True,
            }
        )
        currency_id = (
            cls.env.user.company_id.currency_id
            and cls.env.user.company_id.currency_id.id
            or None
        )

        cls.program_1_id = cls.env["g2p.program.create.wizard"].create(
            {
                "name": "Test Program 1",
                "currency_id": currency_id,
                "amount_per_cycle": 20,
                "amount_per_individual_in_group": 10,
            }
        )

        # Add Program
        program_1_form = cls.program_1_id.create_program()
        program_1_id = program_1_form["res_id"]
        cls.program_1 = cls.env["g2p.program"].search([("id", "=", program_1_id)])
        if cls.program_1:
            _logger.info(
                "Program Testing: Created Program 1 with ID: %s" % cls.program_1.id
            )
        cls.program_2_id = cls.env["g2p.program.create.wizard"].create(
            {
                "name": "Test Program 2",
                "currency_id": currency_id,
                "amount_per_cycle": 100,
                "amount_per_individual_in_group": 10,
            }
        )
        program_2_form = cls.program_2_id.create_program()
        program_2_id = program_2_form["res_id"]
        cls.program_2 = cls.env["g2p.program"].search([("id", "=", program_2_id)])
        if cls.program_2:
            _logger.info(
                "Program Testing: Created Program 2 with ID: %s" % cls.program_2.id
            )

        cls.program_1.write({"target_type": "individual"})
        cls.program_2.write({"target_type": "group"})

        # Add Beneficiaries
        _logger.info(
            "Program Testing: Adding Program: %s, Beneficiaries: %s"
            % (cls.program_1.name, cls.registrant_1.name)
        )
        cls.program_1.write(
            {"program_membership_ids": [(0, 0, {"partner_id": cls.registrant_1.id})]}
        )
        if cls.program_1.program_membership_ids:
            _logger.info(
                "Program Testing: Added Program: %s, Beneficiaries: %s"
                % (
                    cls.program_1.name,
                    cls.program_1.program_membership_ids[0].partner_id.name,
                )
            )

        _logger.info(
            "Program Testing: Adding Program: %s, Beneficiaries (Group): %s"
            % (cls.program_2.name, cls.group_1.name)
        )
        cls.program_2.write(
            {"program_membership_ids": [(0, 0, {"partner_id": cls.group_1.id})]}
        )
        if cls.program_2.program_membership_ids:
            _logger.info(
                "Program Testing: Added Program: %s, Beneficiaries: %s"
                % (
                    cls.program_2.name,
                    cls.program_2.program_membership_ids[0].partner_id.name,
                )
            )

        # Enroll Beneficiaries
        _logger.info(
            "Program Testing: Program %s Beneficiaries Enrollment: %s"
            % (
                cls.program_1.name,
                cls.program_1.program_membership_ids[0].partner_id.name,
            )
        )
        cls.program_1.enroll_eligible_registrants()
        if cls.program_1.program_membership_ids[0].state == "enrolled":
            _logger.info(
                "Program Testing: Program %s Beneficiaries Enrolled: %s"
                % (
                    cls.program_1.name,
                    cls.program_1.program_membership_ids[0].partner_id.name,
                )
            )
        _logger.info(
            "Program Testing: Program %s Beneficiaries Enrollment: %s"
            % (
                cls.program_2.name,
                cls.program_2.program_membership_ids[0].partner_id.name,
            )
        )
        cls.program_2.enroll_eligible_registrants()
        if cls.program_2.program_membership_ids[0].state == "enrolled":
            _logger.info(
                "Program Testing: Program %s Beneficiaries Enrolled: %s"
                % (
                    cls.program_2.name,
                    cls.program_2.program_membership_ids[0].partner_id.name,
                )
            )

        # Create Cycle
        _logger.info("Program Testing: Program %s Creating Cycle" % cls.program_1.name)
        cls.program_1.create_new_cycle()
        _logger.info("Program Testing: Program %s Creating Cycle" % cls.program_2.name)
        cls.program_2.create_new_cycle()
        cls.cycle1 = cls.env["g2p.cycle"].search(
            [("id", "=", cls.program_1.cycle_ids[0].id)]
        )
        if cls.cycle1:
            _logger.info(
                "Program Testing: Added Program: %s, Cycle: %s"
                % (cls.program_1.name, cls.cycle1.name)
            )
        cls.cycle2 = cls.env["g2p.cycle"].search(
            [("id", "=", cls.program_2.cycle_ids[0].id)]
        )
        if cls.cycle2:
            _logger.info(
                "Program Testing: Added Program: %s, Cycle: %s"
                % (cls.program_2.name, cls.cycle2.name)
            )

    def test_01_cycle_prepare_entitlement(self):
        _logger.info(
            "Program Testing: Program: %s, Cycle: %s, Preparing Entitlements"
            % (self.program_1.name, self.cycle1.name)
        )
        self.cycle1.prepare_entitlement()
        message1 = (
            "Program Testing: Program: %s, Cycle: %s, Preparing Entitlements FAILED (EXPECTED %s but RESULT is %s)"
            % (
                self.program_1.name,
                self.cycle1.name,
                1,
                len(self.cycle1.entitlement_ids),
            )
        )
        self.assertEqual(len(self.cycle1.entitlement_ids), 1, message1)
        if len(self.cycle1.entitlement_ids) > 0:
            _logger.info(
                "Program Testing: Program: %s, Cycle: %s, Preparing Entitlements SUCCESS"
                % (self.program_1.name, self.cycle1.name)
            )
        _logger.info(
            "Program Testing: Program: %s, Cycle: %s, Preparing Entitlements"
            % (self.program_2.name, self.cycle2.name)
        )
        self.cycle2.prepare_entitlement()
        message2 = (
            "Program Testing: Program: %s, Cycle: %s, Preparing Entitlements FAILED (EXPECTED %s but RESULT is %s)"
            % (
                self.program_2.name,
                self.cycle2.name,
                1,
                len(self.cycle2.entitlement_ids),
            )
        )
        self.assertEqual(len(self.cycle2.entitlement_ids), 1, message2)
        if len(self.cycle2.entitlement_ids) > 0:
            _logger.info(
                "Program Testing: Program: %s, Cycle: %s, Preparing Entitlements SUCCESS"
                % (self.program_2.name, self.cycle2.name)
            )

        # Check if entitlements_count compute is computing as expected
        _logger.info(
            "Program Testing: Program: %s, Cycle: %s, Checking Entitlements Count %s"
            % (self.program_1.name, self.cycle1.name, self.cycle1.entitlements_count)
        )
        self.assertEqual(self.cycle1.entitlements_count, 1)
        _logger.info(
            "Program Testing: Program: %s, Cycle: %s, Checking Entitlements Count: %s"
            % (self.program_1.name, self.cycle1.name, self.cycle1.entitlements_count)
        )
        self.assertEqual(self.cycle2.entitlements_count, 1)

    def test_02_cycle_approve(self):
        # To Approve
        _logger.info(
            "Program Testing: Program: %s, Cycle: %s, Setting State 'to_approve'"
            % (self.program_1.name, self.cycle1.name)
        )
        self.cycle1.to_approve()
        message1 = (
            "Program Testing: Program: %s, Cycle: %s, Setting State 'to_approve' FAILED (EXPECTED %s but RESULT is %s)"
            % (self.program_1.name, self.cycle1.name, "to_approve", self.cycle1.state)
        )
        self.assertEqual(self.cycle1.state, "to_approve", message1)
        if self.cycle1.state == "to_approve":
            _logger.info(
                "Program Testing: Program: %s, Cycle: %s, Setting State 'to_approve' SUCCESS"
                % (self.program_1.name, self.cycle1.name)
            )
        _logger.info(
            "Program Testing: Program: %s, Cycle: %s, Setting State 'to_approve'"
            % (self.program_2.name, self.cycle2.name)
        )
        self.cycle2.to_approve()
        message2 = (
            "Program Testing: Program: %s, Cycle: %s, Setting State 'to_approve' FAILED (EXPECTED %s but RESULT is %s)"
            % (self.program_2.name, self.cycle2.name, "to_approve", self.cycle2.state)
        )
        self.assertEqual(self.cycle2.state, "to_approve", message2)
        if self.cycle1.state == "to_approve":
            _logger.info(
                "Program Testing: Program: %s, Cycle: %s, Setting State 'to_approve' SUCCESS"
                % (self.program_2.name, self.cycle2.name)
            )

        # Approve
        _logger.info(
            "Program Testing: Program: %s, Cycle: %s, Setting State 'approved'"
            % (self.program_1.name, self.cycle1.name)
        )
        self.cycle1.approve()
        message1 = (
            "Program Testing: Program: %s, Cycle: %s, Setting State 'approved' FAILED (EXPECTED %s but RESULT is %s)"
            % (self.program_1.name, self.cycle1.name, "approved", self.cycle1.state)
        )
        self.assertEqual(self.cycle1.state, "approved")
        if self.cycle1.state == "approved":
            _logger.info(
                "Program Testing: Program: %s, Cycle: %s, Setting State 'approved' SUCCESS"
                % (self.program_1.name, self.cycle1.name)
            )
        _logger.info(
            "Program Testing: Program: %s, Cycle: %s, Setting State 'approved'"
            % (self.program_2.name, self.cycle2.name)
        )
        self.cycle2.approve()
        message2 = (
            "Program Testing: Program: %s, Cycle: %s, Setting State 'approved' FAILED (EXPECTED %s but RESULT is %s)"
            % (self.program_2.name, self.cycle2.name, "approved", self.cycle2.state)
        )
        self.assertEqual(self.cycle2.state, "approved")
        if self.cycle1.state == "approved":
            _logger.info(
                "Program Testing: Program: %s, Cycle: %s, Setting State 'approved' SUCCESS"
                % (self.program_2.name, self.cycle2.name)
            )

    def test_03_deduplication(self):
        _logger.info(
            "Program Testing: Program: %s, Checking Deduplication" % self.program_1.name
        )
        self.program_1.deduplicate_beneficiaries()
        _logger.info(
            "Program Testing: Program: %s, Deduplications Count: %s"
            % (self.program_1.name, self.program_1.duplicate_membership_count)
        )
        _logger.info(
            "Program Testing: Program: %s, Checking Deduplication" % self.program_2.name
        )
        self.program_2.deduplicate_beneficiaries()
        _logger.info(
            "Program Testing: Program: %s, Deduplications Count: %s"
            % (self.program_2.name, self.program_2.duplicate_membership_count)
        )
