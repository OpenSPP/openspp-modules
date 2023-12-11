from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestCreateProgramWiz(TransactionCase):
    def setUp(self):
        super().setUp()
        self._test_products = self.env["product.product"].create(
            [
                {
                    "name": "Flour [TEST]",
                    "detailed_type": "product",
                    "categ_id": self.env.ref("product.product_category_all").id,
                    "uom_id": self.env.ref("uom.product_uom_unit").id,
                    "uom_po_id": self.env.ref("uom.product_uom_unit").id,
                },
                {
                    "name": "Food [TEST]",
                    "detailed_type": "product",
                    "categ_id": self.env.ref("product.product_category_all").id,
                    "uom_id": self.env.ref("uom.product_uom_unit").id,
                    "uom_po_id": self.env.ref("uom.product_uom_unit").id,
                },
            ]
        )
        self._program_create_wiz = self.env["g2p.program.create.wizard"].create(
            {
                "name": "Program 1 [TEST]",
                "rrule_type": "monthly",
                "eligibility_domain": "[]",
                "cycle_duration": 1,
                "currency_id": self.env.company.currency_id.id,
                "entitlement_kind": "inkind",
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
                "entitlement_item_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self._test_products[0].id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self._test_products[-1].id,
                        },
                    ),
                ],
            }
        )

    def test_01_check_required_fields(self):
        with self.assertRaisesRegex(
            UserError,
            "Items are required in the In-kind entitlement manager",
            msg="Missing entitlement items",
        ):
            self._program_create_wiz._check_required_fields()
        self._update_program_create_wiz()
        self._program_create_wiz.write(
            {
                "manage_inventory": True,
                "warehouse_id": None,
            }
        )
        with self.assertRaisesRegex(
            UserError,
            "^For inventory management, the warehouse is required.*$",
            msg="Missing warehouse when managing inventory",
        ):
            self._program_create_wiz._check_required_fields()

    def test_02_get_entitlement_manager(self):
        self._update_program_create_wiz()
        self.assertFalse(
            bool(self.env["g2p.program.entitlement.manager.inkind"].search([])),
            "Start without entitlement manager",
        )
        self.assertFalse(
            bool(self.env["g2p.program.entitlement.manager"].search([])),
            "Start without entitlement manager",
        )
        res = self._program_create_wiz._get_entitlement_manager(self.program.id)
        self.assertTrue(
            bool(self.env["g2p.program.entitlement.manager.inkind"].search([])),
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
