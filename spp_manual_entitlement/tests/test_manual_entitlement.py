from odoo import _
from odoo.tests.common import TransactionCase


class TestManualEntitlement(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.registrant_1 = cls.env["res.partner"].create(
            {
                "name": "Registrant 1 [MANUAL ENTITLEMENT TEST]",
                "is_registrant": True,
                "is_group": True,
            }
        )
        cls.registrant_2 = cls.env["res.partner"].create(
            {
                "name": "Registrant 2 [MANUAL ENTITLEMENT TEST]",
                "is_registrant": True,
                "is_group": True,
            }
        )
        cls.program_wizard = cls.env["g2p.program.create.wizard"].create(
            {
                "name": "Program 1 [MANUAL ENTITLEMENT TEST]",
                "entitlement_kind": "manual_cash",
            }
        )
        cls.program_wizard.create_program()
        cls.program = cls.env["g2p.program"].search([("name", "=", "Program 1 [MANUAL ENTITLEMENT TEST]")])

        membership_vals = [
            {
                "partner_id": cls.registrant_1.id,
                "program_id": cls.program.id,
            },
            {
                "partner_id": cls.registrant_2.id,
                "program_id": cls.program.id,
            },
        ]

        cls.env["g2p.program_membership"].create(membership_vals)
        cls.program.verify_eligibility()
        cls.program.enroll_eligible_registrants()
        cls.program.create_new_cycle()

    def set_cycle(self):
        cycle = self.program.cycle_ids[0]
        cycle.copy_beneficiaries_from_program()
        return cycle

    def test_01_check_manual_entitlement(self):
        cycle = self.set_cycle()

        cycle._compute_is_manual_entitlement()
        self.assertEqual(cycle.is_manual_entitlement, True, "Correct value")
        self.assertFalse(cycle.search_existing_entitlement(self.registrant_1.id), "Correct value")

    def prepare_entitlement_wizard(self, cycle):
        wizard = self.env["spp.manual.entitlement.wizard"].create(
            {
                "cycle_id": cycle.id,
                "step": "step1",
                "cycle_membership_ids": [
                    (0, 0, {"partner_id": self.registrant_1.id, "entitlement_amount": 100, "selected": True})
                ],
            }
        )
        wizard.create_entitlement()
        return wizard

    def test_02_prepare_entitlement_manual(self):
        cycle = self.set_cycle()
        wizard = self.prepare_entitlement_wizard(cycle)
        self.assertTrue(wizard.search_existing_entitlement(self.registrant_1.id), "Correct value")

    def test_03_cycle_prepare_entitlement(self):
        cycle = self.set_cycle()
        prepare_wizard = cycle.prepare_entitlement_manual()
        self.assertEqual(prepare_wizard["res_model"], "spp.manual.entitlement.wizard")

    def test_04_cycle_prepare_entitlement_existing(self):
        cycle = self.set_cycle()
        self.prepare_entitlement_wizard(cycle)
        prepare_wizard = cycle.prepare_entitlement_manual()
        prepare_wizard = self.env["spp.manual.entitlement.wizard"].browse(prepare_wizard["res_id"])
        self.assertEqual(len(prepare_wizard.cycle_membership_ids), 1)

    def test_05_cycle_manager_prepare_async(self):
        cycle = self.set_cycle()
        wizard = self.prepare_entitlement_wizard(cycle)
        wizard_vals = []
        wizard_count = 0
        while wizard_count <= 200:
            wizard_vals.append((0, 0, {"partner_id": self.registrant_1.id, "entitlement_amount": 100}))
            wizard_count += 1
        wizard.write({"cycle_membership_ids": wizard_vals})
        cycle_manager = self.env["g2p.cycle.manager.default"].search([("program_id", "=", self.program.id)])
        cycle_manager.prepare_manual_entitlements(cycle, wizard.cycle_membership_ids)
        self.assertEqual(cycle.locked, True)
        self.assertEqual(cycle.locked_reason, _("Prepare entitlement for beneficiaries."))
