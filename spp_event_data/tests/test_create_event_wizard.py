from datetime import date
from unittest.mock import patch

from odoo.tests import TransactionCase


class TestCreateEventWizard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.registrant = cls.env["res.partner"].create(
            {
                "name": "Test Registrant for Event",
                "is_registrant": True,
            }
        )
        cls.mock_wizard_model_name = "spp.create.event.data.test.wizard"
        cls.mock_model_name = "spp.event.data.test"

    def test_next_page_flow(self):
        """Test the full flow of the create_event_wizard."""
        # Patch the selection field to include our mock model for the test
        selection_patcher = patch.object(
            type(self.env["spp.create.event.wizard"]).event_data_model,
            "selection",
            new=[("default", "None"), (self.mock_model_name, "Test Event")],
        )

        with selection_patcher:
            # Create the wizard *after* the selection field has been patched
            wizard = self.env["spp.create.event.wizard"].create(
                {
                    "event_data_model": self.mock_model_name,
                    "partner_id": self.registrant.id,
                    "registrar": "Test Registrar",
                    "collection_date": date(2024, 1, 15),
                    "expiry_date": date(2025, 1, 15),
                }
            )

            # Create a simple view for the mock wizard model
            self.env["ir.ui.view"].create(
                {
                    "name": "Test Event Data Wizard Form",
                    "type": "form",
                    "model": self.mock_wizard_model_name,
                    "arch_db": """<form string="Test Event Data Wizard"><field name="name"/></form>""",
                }
            )
            action = wizard.next_page()

        # 1. Verify that an spp.event.data record was created with correct values
        event_data = self.env["spp.event.data"].search([("partner_id", "=", self.registrant.id)])
        self.assertEqual(len(event_data), 1, "An spp.event.data record should have been created.")
        self.assertEqual(event_data.model, self.mock_model_name)
        self.assertEqual(event_data.registrar, "Test Registrar")

        # 2. Verify that the action to open the next wizard is correct
        self.assertEqual(action["res_model"], self.mock_wizard_model_name)
        self.assertEqual(action["view_mode"], "form")
        self.assertEqual(action["target"], "new")
        self.assertEqual(action["type"], "ir.actions.act_window")
