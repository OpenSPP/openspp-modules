from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestCreateProgramWiz(TransactionCase):
    def setUp(self):
        super().setUp()
        self._program_create_wiz = self.env["g2p.program.create.wizard"].create(
            {
                "name": "Program 1 [TEST]",
                "rrule_type": "monthly",
                "eligibility_domain": "[]",
                "cycle_duration": 1,
                "currency_id": self.env.company.currency_id.id,
                "entitlement_kind": "cash",
                "max_amount": 5.0,
            }
        )
        self.journal_id = self._program_create_wiz.create_journal(
            self._program_create_wiz.name, self._program_create_wiz.currency_id.id
        )

        self.program = self.env["g2p.program"].create(
            {
                "name": self._program_create_wiz.name,
                "journal_id": self.journal_id,
                "target_type": self._program_create_wiz.target_type,
            }
        )

    def _update_program_create_wiz(self):
        self._program_create_wiz.write(
            {
                "entitlement_cash_item_ids": [
                    (
                        0,
                        0,
                        {
                            "amount": 5.0,
                        },
                    ),
                ],
            }
        )

    def test_01_check_required_fields(self):
        with self.assertRaisesRegex(
            UserError,
            "Items are required in the Cash entitlement manager.",
            msg="Missing entitlement items",
        ):
            self._program_create_wiz._check_required_fields()

    def test_02_get_entitlement_manager(self):
        self._update_program_create_wiz()
        self.assertFalse(
            bool(self.env["g2p.program.entitlement.manager.cash"].search([])),
            "Start without entitlement manager",
        )
        self.assertFalse(
            bool(self.env["g2p.program.entitlement.manager"].search([])),
            "Start without entitlement manager",
        )
        res = self._program_create_wiz._get_entitlement_manager(self.program.id)
        self.assertTrue(
            bool(self.env["g2p.program.entitlement.manager.cash"].search([])),
            "Finish with entitlement manager",
        )
        self.assertTrue(
            bool(self.env["g2p.program.entitlement.manager"].search([])),
            "Finish with entitlement manager",
        )
        self.assertEqual(type(res), dict, "Correct return value")
        self.assertIn("entitlement_managers", res.keys(), "Correct return value")
        self.assertEqual(
            type(res["entitlement_managers"]), list, "Correct return value"
        )
        self.assertEqual(len(res["entitlement_managers"]), 1, "Correct return value")
        self.assertEqual(
            type(res["entitlement_managers"][0]), tuple, "Correct return value"
        )
        self.assertEqual(len(res["entitlement_managers"][0]), 2, "Correct return value")
        self.assertEqual(res["entitlement_managers"][0][0], 4, "Correct return value")
