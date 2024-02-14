from unittest.mock import patch

from odoo.tests import TransactionCase
from odoo.tools import mute_logger


class TestProgram(TransactionCase):
    def setUp(self):
        super().setUp()

        self.program = self.env["g2p.program"].create({"name": "Test Program"})

        manager_default = self.env["g2p.program_membership.manager.default"].create(
            {
                "name": "Default",
                "program_id": self.program.id,
            }
        )
        eligibility_manager = self.env["g2p.eligibility.manager"].create(
            {
                "program_id": self.program.id,
                "manager_ref_id": f"{manager_default._name},{str(manager_default.id)}",
            }
        )
        self.program.update({"eligibility_managers": [(4, eligibility_manager.id)]})

        self.program_2 = self.env["g2p.program"].create({"name": "Test Program 2"})

    @mute_logger("root")
    @patch("odoo.addons.spp_programs.models.programs.len")
    def test_01_import_eligible_registrants(self, mocker):
        mocker.__name__ = "len__mocker"
        action = self.program_2.import_eligible_registrants()

        self.assertEqual(
            [
                action.get("type"),
                action.get("tag"),
                action["params"].get("message"),
                action["params"].get("type"),
            ],
            [
                "ir.actions.client",
                "display_notification",
                "No Eligibility Manager defined.",
                "danger",
            ],
        )

        mocker.return_value = 1
        action_2 = self.program.import_eligible_registrants()

        self.assertEqual(
            [action_2.get("type"), action_2.get("tag"), action_2["params"].get("type")],
            ["ir.actions.client", "display_notification", "success"],
        )

        mocker.return_value = 1000
        action_3 = self.program.import_eligible_registrants()

        self.assertEqual(
            [action_3.get("type"), action_3.get("tag"), action_3["params"].get("type")],
            ["ir.actions.client", "display_notification", "success"],
        )
