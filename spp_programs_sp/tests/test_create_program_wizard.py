from odoo.tests.common import TransactionCase


class CreateProgramWizardTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._program_create_wiz = cls.env["g2p.program.create.wizard"].create(
            {
                "name": "Program 1 [TEST]",
                "rrule_type": "monthly",
                "eligibility_domain": "[]",
                "cycle_duration": 1,
                "currency_id": cls.env.company.currency_id.id,
                "amount_per_cycle": 1.0,
                "store_sp_in_entitlements": True,
            }
        )

    def test_get_program_vals(self):
        vals = self._program_create_wiz.get_program_vals()

        self.assertIn("store_sp_in_entitlements", vals)
        self.assertTrue(vals["store_sp_in_entitlements"])
