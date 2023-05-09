from unittest.mock import Mock, patch

from odoo import Command, fields
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestEntitlement(TransactionCase):
    def setUp(self):
        super().setUp()

        self.program = self.env["g2p.program"].create({"name": "Test Program"})

        registrant = self.env["res.partner"].create(
            {
                "name": "test registrant",
                "is_registrant": True,
            }
        )

        self.cycle = self.env["g2p.cycle"].create(
            {
                "name": "Test Cycle",
                "program_id": self.program.id,
                "start_date": fields.Date.today(),
                "end_date": fields.Date.today(),
            }
        )

        self.entitlement = self.env["g2p.entitlement.inkind"].create(
            {
                "partner_id": registrant.id,
                "cycle_id": self.cycle.id,
            }
        )
        group = [
            Command.link(self.env.ref("g2p_programs.g2p_program_manager").id),
        ]
        self.test_user_1 = self.env["res.users"].create(
            {"name": "test", "login": "test", "groups_id": group}
        )

        group_2 = [
            Command.link(self.env.ref("g2p_programs.g2p_program_manager").id),
            Command.link(self.env.ref("g2p_registry_base.group_g2p_registrar").id),
        ]
        self.test_user_2 = self.env["res.users"].create(
            {"name": "test2", "login": "test2", "groups_id": group_2}
        )

    def test_01_generate_code(self):
        self.assertIsNotNone(self.entitlement._generate_code())

    def test_02_fields_view_get(self):
        action_1 = self.entitlement.fields_view_get(view_type="form")
        action_2 = self.entitlement.with_user(self.test_user_1.id).fields_view_get(
            view_type="form"
        )
        action_3 = self.entitlement.with_user(self.test_user_1.id).fields_view_get(
            view_type="search"
        )

        self.assertTrue(all([action_1, action_2, action_3]))

        with self.assertRaisesRegex(
            ValidationError, "You have no access in the Entitlement List View"
        ):
            self.entitlement.with_user(self.test_user_2.id).fields_view_get(
                view_type="form"
            )

    def test_03_compute_journal_id(self):
        self.entitlement._compute_journal_id()
        self.assertEqual(self.entitlement.journal_id.id, self.program.journal_id.id)

    def test_04_compute_name(self):
        self.entitlement._compute_name()

        self.assertEqual(
            self.entitlement.name, f"Entitlement: ({self.entitlement.product_id.name})"
        )

    def test_05_gc_mark_expired_entitlement(self):
        # Check if function doesn't have error

        self.entitlement._gc_mark_expired_entitlement()

    def test_06_unlink(self):
        self.entitlement.state = "pending_validation"

        with self.assertRaisesRegex(
            ValidationError, "Only draft entitlements are allowed to be deleted"
        ):
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

    @patch(
        "odoo.addons.spp_programs.models.entitlement.InKindEntitlement._get_outgoing_incoming_moves"
    )
    def test_10_get_qty_procurement(self, mocker):
        pass
