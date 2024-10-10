from unittest.mock import patch

from odoo.tests.common import TransactionCase

from ..tools.rsa_encode_decode import calculate_signature, verify_and_decode_signature


class TestRSA(TransactionCase):
    pass
    # @patch("odoo.addons.spp_oauth.tools.rsa_encode_decode.jwt.encode")
    # def test_calculate_signature(self, mock_encode):
    #     mock_encode.return_value = "mocked_signature"
    #
    #     header = {"typ": "JWT"}
    #     payload = {"data": "test"}
    #     signature = calculate_signature(header, payload)
    # 
    #     self.assertEqual(signature, "mocked_signature")
    #
    # @patch("odoo.addons.spp_oauth.tools.rsa_encode_decode.jwt.decode")
    # def test_verify_and_decode_signature(self, mock_decode):
    #     mock_decode.return_value = {"data": "test"}
    #
    #     access_token = "mocked_access_token"
    #
    #     decoded = verify_and_decode_signature(access_token)
    #
    #     self.assertEqual(decoded, {"data": "test"})
