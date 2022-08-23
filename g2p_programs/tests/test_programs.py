import logging

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class ProgramTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
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
        cls.program_1.write({"target_type": "individual"})
        cls.program_2.write({"target_type": "group"})

        # Add Beneficiaries
        cls.program_1.write(
            {"program_membership_ids": [(0, 0, {"partner_id": cls.registrant_1.id})]}
        )
        cls.program_2.write(
            {"program_membership_ids": [(0, 0, {"partner_id": cls.group_1.id})]}
        )
        # Enroll Beneficiaries
        cls.program_1.enroll_eligible_registrants()
        cls.program_2.enroll_eligible_registrants()
        cls.program_1.create_new_cycle()
        cls.program_2.create_new_cycle()
        cls.cycle1 = cls.env["g2p.cycle"].search(
            [("id", "=", cls.program_1.cycle_ids[0].id)]
        )
        cls.cycle2 = cls.env["g2p.cycle"].search(
            [("id", "=", cls.program_2.cycle_ids[0].id)]
        )

    def test_01_cycle_prepare_entitlement(self):
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
        # Check if entitlements_count compute is computing as expected
        self.assertEqual(self.cycle1.entitlements_count, 1)
        self.assertEqual(self.cycle2.entitlements_count, 1)

    def test_02_cycle_approve(self):
        # To Approve
        user = self.env.user

        # Add Super User to Cycle Approver Group
        approver_group = self.env["res.groups"].search(
            [("id", "=", self.env.ref("g2p_programs.g2p_program_cycle_approver").id)]
        )

        approver_group.write({"users": [(4, user.id)]})

        manager_ref_id = str(self.program_1.cycle_managers[0].manager_ref_id)
        s = manager_ref_id.find("(")
        res_model = manager_ref_id[:s]
        res_id = self.program_1.cycle_managers[0].manager_ref_id.id
        approver = self.env[res_model].search([("id", "=", res_id)])
        group = self.env.ref("g2p_programs.g2p_program_cycle_approver").id
        approver.approver_group_id = group

        manager_ref_id = str(self.program_2.cycle_managers[0].manager_ref_id)
        s = manager_ref_id.find("(")
        res_model = manager_ref_id[:s]
        res_id = self.program_2.cycle_managers[0].manager_ref_id.id
        approver = self.env[res_model].search([("id", "=", res_id)])
        group = self.env.ref("g2p_programs.g2p_program_cycle_approver").id
        approver.approver_group_id = group

        self.cycle1.to_approve()
        message1 = (
            "Program Testing: Program: %s, Cycle: %s, Setting State 'to_approve' FAILED (EXPECTED %s but RESULT is %s)"
            % (self.program_1.name, self.cycle1.name, "to_approve", self.cycle1.state)
        )
        self.assertEqual(self.cycle1.state, "to_approve", message1)
        self.cycle2.to_approve()
        message2 = (
            "Program Testing: Program: %s, Cycle: %s, Setting State 'to_approve' FAILED (EXPECTED %s but RESULT is %s)"
            % (self.program_2.name, self.cycle2.name, "to_approve", self.cycle2.state)
        )
        self.assertEqual(self.cycle2.state, "to_approve", message2)
        # Approve
        self.cycle1.approve()
        message1 = (
            "Program Testing: Program: %s, Cycle: %s, Setting State 'approved' FAILED (EXPECTED %s but RESULT is %s)"
            % (self.program_1.name, self.cycle1.name, "approved", self.cycle1.state)
        )
        self.assertEqual(self.cycle1.state, "approved")
        self.cycle2.approve()
        message2 = (
            "Program Testing: Program: %s, Cycle: %s, Setting State 'approved' FAILED (EXPECTED %s but RESULT is %s)"
            % (self.program_2.name, self.cycle2.name, "approved", self.cycle2.state)
        )
        self.assertEqual(self.cycle2.state, "approved")

    def test_03_deduplication(self):
        self.program_1.deduplicate_beneficiaries()
        self.assertEqual(
            self.program_1.duplicate_membership_count,
            0,
            "Program Testing: Expected Duplicate count exceeded",
        )
        self.program_2.deduplicate_beneficiaries()
        self.assertEqual(
            self.program_2.duplicate_membership_count,
            0,
            "Program Testing: Expected Duplicate count exceeded",
        )
