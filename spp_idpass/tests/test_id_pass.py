from unittest.mock import Mock, patch

from odoo.tests import TransactionCase


class TestIdPass(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._id_pass = cls.env["spp.id.pass"].create(
            {
                "name": "Test ID Pass",
                "auth_token_url": "https://auth.token.url",
                "api_username": "Username",
                "api_password": "P@$$w0rd",
            }
        )

    @patch("requests.post")
    def test_01_generate_auth_token_response_200(self, mock_post):
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {"token": "Testing token - for testing purpose!"},
        )
        self._id_pass.generate_auth_token()
        self.assertEqual(
            self._id_pass.auth_token,
            "Testing token - for testing purpose!",
            "auth token of ID Pass should have the same value with return token from json params",
        )

    @patch("requests.post")
    def test_02_generate_auth_token_response_403(self, mock_post):
        mock_post.return_value = Mock(
            status_code=403,
            json=lambda: {"token": "Testing token - for testing purpose!"},
        )
        self._id_pass.generate_auth_token()
        self.assertFalse(self._id_pass.auth_token, "auth token of ID Pass should not have data")
