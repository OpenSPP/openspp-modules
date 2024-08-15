import uuid

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class ClientCredentialsTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """
        Setup and create necessary records for this test
        """
        super().setUpClass()

        cls.dci_api_model = cls.env["spp.dci.api.client.credential"]

    def test_generate_client_id(self):
        client_id = self.dci_api_model._generate_client_id()
        self.assertTrue(bool(uuid.UUID(client_id)))

    def test_generate_client_secret(self):
        client_secret = self.dci_api_model._generate_client_secret()
        self.assertTrue(bool(uuid.UUID(client_secret)))

    def test_show_credentials(self):
        api_id = self.dci_api_model.create(
            {
                "name": "Test API Client",
            }
        )

        self.assertFalse(api_id.show_button_clicked)

        action = api_id.show_credentials()

        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "spp.dci.api.client.credential")
        self.assertEqual(
            action["views"][0][0], self.env.ref("spp_dci_api_server.spp_dci_api_client_credential_view_credentials").id
        )
        self.assertEqual(action["target"], "new")
        self.assertEqual(action["res_id"], api_id.id)
        self.assertEqual(action["view_type"], "form")
        self.assertEqual(action["view_mode"], "form")
        self.assertTrue(api_id.show_button_clicked)

        with self.assertRaisesRegex(UserError, "Client ID and Client Secret is already showed once."):
            api_id.show_credentials()
