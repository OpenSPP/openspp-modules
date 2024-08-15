from unittest.mock import patch

from odoo.tests.common import TransactionCase

from ..tools.rsa_encode_decode import calculate_signature, verify_and_decode_signature


class TestRSA(TransactionCase):
    @patch("odoo.addons.spp_oauth.tools.rsa_encode_decode.jwt.encode")
    def test_calculate_signature(self, mock_encode):
        mock_encode.return_value = "mocked_signature"

        header = {"typ": "JWT"}
        payload = {"data": "test"}
        signature = calculate_signature(header, payload)

        self.assertEqual(signature, "mocked_signature")
        mock_encode.assert_called_once_with(headers=header, payload=payload, key="", algorithm="RS256")

    @patch("odoo.addons.spp_oauth.tools.rsa_encode_decode.jwt.decode")
    def test_verify_and_decode_signature(self, mock_decode):
        mock_decode.return_value = {"data": "test"}

        access_token = "mocked_access_token"

        success, decoded = verify_and_decode_signature(access_token)

        self.assertTrue(success)
        self.assertEqual(decoded, {"data": "test"})
        mock_decode.assert_called_once_with(access_token, key="", algorithms=["RS256"])
