from odoo import fields
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
        cls.program_wizard = cls.env["g2p.program.create.wizard"].create(
            {
                "name": "Program 1 [MANUAL ENTITLEMENT TEST]",
                "entitlement_kind": "manual_cash",
            }
        )
        cls.program_wizard.create_program()
        cls.program = cls.env["g2p.program"].search([("name", "=", "Program 1 [MANUAL ENTITLEMENT TEST]")])

        membership_vals = {
            "partner_id": cls.registrant_1.id,
            "program_id": cls.program.id,
            "state": "enrolled",
            "enrollment_date": fields.Datetime.now(),
        }
        cls.env["g2p.program_membership"].create(membership_vals)
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

    def test_02_prepare_entitlement_manual(self):
        cycle = self.set_cycle()
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
        self.assertTrue(wizard.search_existing_entitlement(self.registrant_1.id), "Correct value")
