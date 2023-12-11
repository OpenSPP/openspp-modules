from odoo.tests import TransactionCase


class TestResUser(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = cls.env["res.users"].create(
            {
                "name": "TestUserResUser",
                "login": "test_user_res_user",
                "password": "test_user_res_user",
            }
        )

    def test_01_reset_openapi_token(self):
        self.user.reset_openapi_token()

        self.assertIsNotNone(self.user.openapi_token)

    def test_02_get_unique_openapi_token(self):
        self.user._get_unique_openapi_token()

        self.assertIsNotNone(self.user.openapi_token)

    def test_03_reset_all_openapi_tokens(self):
        self.env["res.users"].reset_all_openapi_tokens()

        self.assertIsNotNone(self.user.openapi_token)
