import uuid

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class ApiClientCredentialsTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """
        Setup and create necessary records for this test
        """
        super().setUpClass()
        cls.gis_api_model = cls.env["spp.gis.api.client.credential"]

    def test_generate_client_id(self):
        client_id = self.gis_api_model._generate_client_id()
        self.assertTrue(bool(uuid.UUID(client_id)))

    def test_generate_client_secret(self):
        client_secret = self.gis_api_model._generate_client_secret()
        self.assertTrue(bool(uuid.UUID(client_secret)))

    def test_generate_client_token(self):
        client_token = self.gis_api_model._generate_client_token()
        self.assertTrue(bool(uuid.UUID(client_token)))

    def test_show_credentials(self):
        api_id = self.gis_api_model.create(
            {
                "name": "Test API Client",
                "auth_type": "bearer",
            }
        )

        self.assertFalse(api_id.show_button_clicked)
        action = api_id.show_credentials()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "spp.gis.api.client.credential")
        self.assertEqual(
            action["views"][0][0], self.env.ref("spp_base_gis_rest.spp_gis_api_client_credential_view_credentials").id
        )
        self.assertEqual(action["target"], "new")
        self.assertEqual(action["res_id"], api_id.id)
        self.assertEqual(action["view_type"], "form")
        self.assertEqual(action["view_mode"], "form")
        self.assertTrue(api_id.show_button_clicked)

        with self.assertRaisesRegex(UserError, "Client ID and Client Secret is already showed once."):
            api_id.show_credentials()

    def test_export_data(self):
        api_id = self.gis_api_model.create(
            {
                "name": "Test API Client",
                "auth_type": "bearer",
            }
        )

        with self.assertRaisesRegex(UserError, "Not allowed to export on this model."):
            api_id.export_data([])
