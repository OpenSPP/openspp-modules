from uuid import UUID

from odoo.tests.common import TransactionCase


class TestResUsers(TransactionCase):
    def setUp(self):
        super().setUp()
        # Get the main company
        main_company = self.env.ref("base.main_company")

        # Create user with all required fields
        self.user = (
            self.env["res.users"]
            .with_context(
                no_reset_password=True,  # Prevent password reset emails
                company_id=main_company.id,
            )
            .create(
                {
                    "name": "Test API User",
                    "login": "test_api_user",
                    "company_id": main_company.id,
                    "company_ids": [(4, main_company.id)],
                    "partner_id": self.env["res.partner"]
                    .create(
                        {
                            "name": "Test API User",
                            "company_id": main_company.id,
                        }
                    )
                    .id,
                }
            )
        )

    def test_openapi_token_default(self):
        """Test that a new user gets a valid UUID token by default"""
        # Verify token is a valid UUID
        token = UUID(self.user.openapi_token)
        self.assertTrue(token.version == 4)

    def test_reset_openapi_token(self):
        """Test token reset functionality"""
        old_token = self.user.openapi_token
        self.user.reset_openapi_token()
        new_token = self.user.openapi_token

        # Verify tokens are different
        self.assertNotEqual(old_token, new_token)
        # Verify new token is a valid UUID
        token = UUID(new_token)
        self.assertTrue(token.version == 4)

    def test_reset_all_openapi_tokens(self):
        """Test mass token reset functionality"""
        initial_token = self.user.openapi_token
        self.env["res.users"].reset_all_openapi_tokens()
        self.assertNotEqual(initial_token, self.user.openapi_token)

    def test_action_view_bearer_token(self):
        """Test bearer token wizard action"""
        action = self.user.action_view_bearer_token()

        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "spp.users.bearer.token")
        self.assertEqual(action["target"], "new")

        # Verify token was created
        token = self.env["spp.users.bearer.token"].browse(action["res_id"])
        self.assertEqual(token.user_id, self.user)
