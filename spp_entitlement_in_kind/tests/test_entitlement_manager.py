from datetime import date
from unittest.mock import patch

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestEntitlementManager(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._test_products = cls.env["product.product"].create(
            [
                {
                    "name": "Flour [TEST]",
                    "detailed_type": "product",
                    "categ_id": cls.env.ref("product.product_category_all").id,
                    "uom_id": cls.env.ref("uom.product_uom_unit").id,
                    "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                },
                {
                    "name": "Food [TEST]",
                    "detailed_type": "product",
                    "categ_id": cls.env.ref("product.product_category_all").id,
                    "uom_id": cls.env.ref("uom.product_uom_unit").id,
                    "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                },
            ]
        )
        country = cls.env.ref("base.iq")
        cls.service_points = cls.env["spp.service.point"].create(
            [
                {
                    "name": "Correct Phone Number",
                    "country_id": country.id,
                    "phone_no": "+9647001234567",
                    "is_disabled": False,
                },
                {
                    "name": "In-correct Phone Number",
                    "country_id": country.id,
                    "phone_no": "+964700123456",
                    "is_disabled": True,
                    "disabled_reason": "Wrong phone number format!",
                },
            ]
        )
        cls.registrants = cls.env["res.partner"].create(
            [
                {
                    "name": "Registrant 1 [TEST]",
                    "is_registrant": True,
                    "is_group": True,
                    "service_point_ids": [(6, 0, cls.service_points.ids)],
                },
                {
                    "name": "Registrant 2 [TEST]",
                    "is_registrant": True,
                    "is_group": True,
                    "service_point_ids": [(6, 0, cls.service_points.ids)],
                },
            ]
        )
        cls.program = cls.env["g2p.program"].create(
            {
                "name": "Program 1 [TEST]",
                "program_membership_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": cls.registrants[0].id,
                            "state": "enrolled",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "partner_id": cls.registrants[-1].id,
                            "state": "enrolled",
                        },
                    ),
                ],
            }
        )
        cls.cycle = cls.env["g2p.cycle"].create(
            {
                "name": "Cycle 1 [TEST]",
                "program_id": cls.program.id,
                "start_date": fields.Date.today(),
                "end_date": fields.Date.today(),
            }
        )
        cls._inkind_entitlement_manager = cls.env["g2p.program.entitlement.manager.inkind"].create(
            {
                "name": "Entitlement Manager Inkind 1 [TEST]",
                "program_id": cls.program.id,
                "warehouse_id": cls.env.ref("stock.warehouse0").id,
            }
        )

    def create_entitlement_inkind(self):
        return self.env["g2p.entitlement.inkind"].create(
            {
                "partner_id": self.registrants[0].id,
                "cycle_id": self.cycle.id,
                "product_id": self._test_products[0].id,
                "valid_from": fields.Date.today(),
            }
        )

    def test_01_prepare_entitlements(self):
        with self.assertRaisesRegex(UserError, "no items entered for this"):
            self._inkind_entitlement_manager.prepare_entitlements(self.cycle, self.program.program_membership_ids)
        self._inkind_entitlement_manager.write(
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
        before_entitlement_inkind = self.env["g2p.entitlement.inkind"].search([])
        self.assertFalse(before_entitlement_inkind.ids, "Start without entitlement inkind!")
        self._inkind_entitlement_manager.prepare_entitlements(self.cycle, self.program.program_membership_ids)
        after_entitlement_inkind = self.env["g2p.entitlement.inkind"].search([])
        self.assertTrue(bool(after_entitlement_inkind.ids), "Entitlement Inkind should be created!")

    def test_02_set_pending_validation_entitlements(self):
        entitlement = self.create_entitlement_inkind()
        entitlement.state = "draft"
        self._inkind_entitlement_manager.set_pending_validation_entitlements(self.cycle)
        self.assertEqual(
            entitlement.state,
            "pending_validation",
            "Entitlement now should be pending validation!",
        )

    @patch("odoo.fields.Date.today")
    def test_03_validate_entitlements(self, mock_today):
        mock_today.__name__ = "mock_today"
        mock_today.return_value = date(2023, 5, 23)
        entitlement = self.create_entitlement_inkind()
        res = self._inkind_entitlement_manager.validate_entitlements(self.cycle)
        self.assertEqual(res["params"]["type"], "success", "Should display success notification!")
        self.assertEqual(entitlement.state, "approved", "Entitlement should now approved!")
        self.assertEqual(
            entitlement.date_approved,
            date(2023, 5, 23),
            "Entitlement approving date should be today!",
        )

    def test_04_cancel_entitlements(self):
        entitlement = self.create_entitlement_inkind()
        self._inkind_entitlement_manager.cancel_entitlements(self.cycle)
        self.assertEqual(entitlement.state, "cancelled", "Entitlement should now cancelled!")

    def test_05_open_entitlements_form(self):
        res = self._inkind_entitlement_manager.open_entitlements_form(self.cycle)
        for key in ["res_model", "type", "domain"]:
            self.assertIn(key, res.keys(), f"Key `{key}` is missing from return action!")
        self.assertEqual(res["res_model"], "g2p.entitlement.inkind")
        self.assertEqual(res["type"], "ir.actions.act_window")
        self.assertEqual(res["domain"], [("cycle_id", "=", self.cycle.id)])

    def test_06_open_entitlement_form(self):
        entitlement = self.create_entitlement_inkind()
        res = self._inkind_entitlement_manager.open_entitlement_form(entitlement)
        for key in ["res_model", "type", "target", "res_id", "view_mode"]:
            self.assertIn(key, res.keys(), f"Key `{key}` is missing from return action!")
        self.assertEqual(res["res_model"], "g2p.entitlement.inkind")
        self.assertEqual(res["type"], "ir.actions.act_window")
        self.assertEqual(res["target"], "new")
        self.assertEqual(res["res_id"], entitlement.id)
        self.assertEqual(res["view_mode"], "form")
