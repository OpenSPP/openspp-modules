from odoo.exceptions import UserError

from .common import Common


class TestCreateProgramWiz(Common):
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
                "entitlement_kind": "basket_entitlement",
            }
        )

    def test_01_onchange_entitlement_kind(self):
        self._program_create_wiz.target_type = "individual"
        self._program_create_wiz._onchange_entitlement_kind()
        self.assertEqual(
            self._program_create_wiz.target_type,
            "group",
            "Entitlement kind should change target!",
        )

    def test_02_onchange_entitlement_basket_id(self):
        self.assertFalse(
            self._program_create_wiz.basket_entitlement_item_ids.ids,
            "Start without basket entitlement items!",
        )
        self._program_create_wiz.entitlement_basket_id = self.env["spp.entitlement.basket"].create(
            {
                "name": "Basket 1 [TEST]",
                "product_ids": [
                    (
                        0,
                        0,
                        {"product_id": self._test_products[0].id},
                    ),
                    (
                        0,
                        0,
                        {"product_id": self._test_products[-1].id},
                    ),
                ],
            }
        )
        self._program_create_wiz._onchange_entitlement_basket_id()
        self.assertTrue(
            self._program_create_wiz.basket_entitlement_item_ids.ids,
            "Ends with basket entitlement items!",
        )

    def test_03_check_required_fields(self):
        with self.assertRaisesRegex(UserError, "Food Basket in Cycle Manager is required"):
            self._program_create_wiz._check_required_fields()
        self._program_create_wiz.entitlement_basket_id = self.env["spp.entitlement.basket"].create(
            {
                "name": "Basket 1 [TEST]",
            }
        )
        with self.assertRaisesRegex(UserError, "Items are required"):
            self._program_create_wiz._check_required_fields()
        self._program_create_wiz.write(
            {
                "manage_inventory": True,
                "warehouse_id": None,
                "basket_product_ids": [(6, 0, self._test_products.ids)],
            }
        )
        with self.assertRaisesRegex(UserError, "For inventory management, the warehouse is required"):
            self._program_create_wiz._check_required_fields()

    def test_04_get_entitlement_manager(self):
        self._program_create_wiz.entitlement_basket_id = self.env["spp.entitlement.basket"].create(
            {
                "name": "Basket 1 [TEST]",
                "product_ids": [
                    (
                        0,
                        0,
                        {"product_id": self._test_products[0].id},
                    ),
                    (
                        0,
                        0,
                        {"product_id": self._test_products[-1].id},
                    ),
                ],
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
        self.assertFalse(
            bool(self.env["g2p.program.entitlement.manager.basket"].search([])),
            "Start without entitlement manager",
        )
        self.assertFalse(
            bool(self.env["g2p.program.entitlement.manager"].search([])),
            "Start without entitlement manager",
        )
        res = self._program_create_wiz._get_entitlement_manager(self.program.id)
        self.assertTrue(
            bool(self.env["g2p.program.entitlement.manager.basket"].search([])),
            "Finish with entitlement manager",
        )
        self.assertTrue(
            bool(self.env["g2p.program.entitlement.manager"].search([])),
            "Finish with entitlement manager",
        )
        self.assertEqual(type(res), dict, "Correct return value")
        self.assertIn("entitlement_managers", res.keys(), "Correct return value")
        self.assertEqual(type(res["entitlement_managers"]), list, "Correct return value")
        self.assertEqual(len(res["entitlement_managers"]), 1, "Correct return value")
        self.assertEqual(type(res["entitlement_managers"][0]), tuple, "Correct return value")
        self.assertEqual(len(res["entitlement_managers"][0]), 2, "Correct return value")
        self.assertEqual(res["entitlement_managers"][0][0], 4, "Correct return value")
