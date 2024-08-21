from datetime import date
from unittest.mock import Mock, patch

from odoo import Command, fields
from odoo.exceptions import UserError, ValidationError
from odoo.tools import mute_logger

from .common import Common


class TestEntitlement(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        group = [
            Command.link(cls.env.ref("g2p_programs.g2p_program_manager").id),
        ]
        cls.test_user_1 = cls.env["res.users"].create({"name": "test", "login": "test", "groups_id": group})

        group_2 = [
            Command.link(cls.env.ref("g2p_programs.g2p_program_manager").id),
            Command.link(cls.env.ref("g2p_registry_base.group_g2p_registrar").id),
        ]
        cls.test_user_2 = cls.env["res.users"].create({"name": "test2", "login": "test2", "groups_id": group_2})

    def test_01_generate_code(self):
        self.assertIsNotNone(self.entitlement._generate_code())

    def test_02_get_view(self):
        action_1 = self.entitlement._get_view(view_type="form")
        action_2 = self.entitlement.with_user(self.test_user_1.id)._get_view(view_type="form")
        action_3 = self.entitlement.with_user(self.test_user_1.id)._get_view(view_type="search")

        self.assertTrue(all([action_1, action_2, action_3]))

        with self.assertRaisesRegex(ValidationError, "You have no access in the Entitlement List View"):
            self.entitlement.with_user(self.test_user_2.id)._get_view(view_type="form")

    def test_03_compute_journal_id(self):
        self.entitlement._compute_journal_id()
        self.assertEqual(self.entitlement.journal_id.id, self.program.journal_id.id)

    def test_04_compute_name(self):
        self.entitlement._compute_name()

        self.assertEqual(self.entitlement.name, f"Entitlement: ({self.entitlement.product_id.name})")

    @patch("odoo.fields.Date.today")
    def test_05_gc_mark_expired_entitlement(self, mocked_today):
        mocked_today.__name__ = "today_mock"
        mocked_today.return_value = date(2023, 5, 20)
        entitlement_to_expired = self.env["g2p.entitlement"].create(
            [
                {
                    "partner_id": self.registrant.id,
                    "initial_amount": 1.0,
                    "cycle_id": self.cycle.id,
                    "state": "approved",
                    "valid_until": fields.Date.add(fields.Date.today(), days=-1),
                },
                {
                    "partner_id": self.registrant.id,
                    "initial_amount": 1.0,
                    "cycle_id": self.cycle.id,
                    "state": "approved",
                    "valid_until": fields.Date.add(fields.Date.today(), days=-1),
                },
                {
                    "partner_id": self.registrant.id,
                    "initial_amount": 1.0,
                    "cycle_id": self.cycle.id,
                    "state": "approved",
                    "valid_until": fields.Date.add(fields.Date.today(), days=-1),
                },
            ]
        )
        entitlement_not_to_expired = self.env["g2p.entitlement"].create(
            [
                {
                    "partner_id": self.registrant.id,
                    "initial_amount": 1.0,
                    "cycle_id": self.cycle.id,
                    "state": "approved",
                    "valid_until": fields.Date.add(fields.Date.today(), days=1),
                },
                {
                    "partner_id": self.registrant.id,
                    "initial_amount": 1.0,
                    "cycle_id": self.cycle.id,
                    "state": "approved",
                    "valid_until": fields.Date.add(fields.Date.today(), days=1),
                },
                {
                    "partner_id": self.registrant.id,
                    "initial_amount": 1.0,
                    "cycle_id": self.cycle.id,
                    "state": "approved",
                    "valid_until": fields.Date.add(fields.Date.today(), days=1),
                },
            ]
        )
        self.entitlement._gc_mark_expired_entitlement()
        for rec in entitlement_to_expired:
            self.assertEqual(
                rec.state,
                "expired",
                "To expired entitlement should be expired after garbage collector run!",
            )
        for rec in entitlement_not_to_expired:
            self.assertNotEqual(
                rec.state,
                "expired",
                "Not to expired entitlement should not be expired!",
            )

    @mute_logger("odoo.models.unlink")
    def test_06_unlink(self):
        self.entitlement.state = "pending_validation"

        with self.assertRaisesRegex(ValidationError, "Only draft entitlements are allowed to be deleted"):
            self.entitlement.unlink()

        self.entitlement.state = "draft"
        action = self.entitlement.unlink()
        self.assertIsNotNone(action)

    @patch("odoo.addons.g2p_programs.models.programs.G2PProgram.get_manager")
    def test_07_approve_entitlement(self, mocker):
        mocker.__name__ = "mocker__get_manager"

        manager_mock = Mock()
        manager_mock.approve_entitlements.return_value = (1, "Error Message")

        mocker.return_value = manager_mock
        action = self.entitlement.approve_entitlement()

        self.assertEqual(
            [
                action.get("type"),
                action.get("tag"),
                action["params"].get("type"),
                action["params"].get("message"),
            ],
            ["ir.actions.client", "display_notification", "danger", "Error Message"],
        )

    @patch("odoo.addons.g2p_programs.models.programs.G2PProgram.get_manager")
    def test_08_open_entitlement_form(self, mocker):
        mocker.__name__ = "mocker__get_manager"

        manager_mock = Mock()
        manager_mock.open_entitlement_form.return_value = True

        mocker.return_value = manager_mock

        self.assertTrue(self.entitlement.open_entitlement_form())

    def test_09_prepare_procurement_values(self):
        vals = self.entitlement._prepare_procurement_values()

        self.assertEqual(
            [vals.get("date_planned"), vals.get("date_deadline")],
            [self.cycle.start_date, self.cycle.end_date],
        )

    def test_10_get_qty_procurement(self):
        self.entitlement.product_id = self.env["product.product"].create(
            {
                "name": "Flour [TEST]",
                "detailed_type": "product",
                "categ_id": self.env.ref("product.product_category_all").id,
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "uom_po_id": self.env.ref("uom.product_uom_unit").id,
            }
        )
        self.entitlement.uom_id = self.env.ref("uom.product_uom_unit")
        self.assertEqual(
            self.entitlement._get_qty_procurement(),
            0.0,
            "Procurement Quantity should be 0 since no move in or out!",
        )
        self.env["stock.move"].create(
            {
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.env.ref("stock.stock_location_stock").id,
                "to_refund": True,
                "name": "Test Move In - Flour [TEST]",
                "product_id": self.entitlement.product_id.id,
                "date": fields.Date.today(),
                "product_uom": self.env.ref("uom.product_uom_unit").id,
                "product_uom_qty": 1.0,
                "entitlement_id": self.entitlement.id,
            }
        )
        self.assertEqual(
            self.entitlement._get_qty_procurement(),
            -1.0,
            "Procurement Quantity should be -1 since there is a refund move in!",
        )
        self.env["stock.move"].create(
            {
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                "to_refund": True,
                "name": "Test Move Out - Flour [TEST]",
                "product_id": self.entitlement.product_id.id,
                "date": fields.Date.today(),
                "product_uom": self.env.ref("uom.product_uom_unit").id,
                "product_uom_qty": 2.0,
                "entitlement_id": self.entitlement.id,
            }
        )
        self.assertEqual(
            self.entitlement._get_qty_procurement(),
            1.0,
            "Procurement Quantity should be 1 since there is a refund move out!",
        )

    def test_11_prepare_procurement_group_vals(self):
        vals = self.entitlement._prepare_procurement_group_vals()
        self.assertEqual(vals["name"], "Test Cycle", "Name should be cycle name!")
        self.assertEqual(vals["move_type"], "direct", "Move type should be direct!")
        self.assertEqual(
            vals["cycle_id"],
            self.entitlement.cycle_id.id,
            "Cycle should be entitlement cycle!",
        )
        self.assertEqual(
            vals["partner_id"],
            self.entitlement.partner_id.id,
            "Partner Id should be entitlement partner!",
        )

    def test_12_approve_entitlement(self):
        entitlement_id = self.env["g2p.entitlement"].create(
            {
                "partner_id": self.registrant.id,
                "initial_amount": 1.0,
                "cycle_id": self.cycle.id,
                "state": "approved",
                "valid_until": fields.Date.add(fields.Date.today(), days=1),
            }
        )
        entitlement_state = entitlement_id.state
        with self.assertRaisesRegex(ValidationError, "The cycle must be approved before approving entitlement"):
            entitlement_id.approve_entitlement()
        self.assertEqual(entitlement_id.state, entitlement_state)

        self.cycle.write({"state": "approved"})
        with self.assertRaisesRegex(UserError, "No Entitlement Manager defined."):
            entitlement_id.approve_entitlement()
