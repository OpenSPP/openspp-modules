from unittest.mock import patch

from odoo.tests.common import TransactionCase


class EncryptionProviderTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.provide_no_type = cls.env["g2p.encryption.provider"].create({"name": "Test Provider"})
        cls.provider = cls.env["g2p.encryption.provider"].create(
            {"name": "Test Provider with Type", "type": "jwcrypto"}
        )
        cls.provider_with_key = cls.env["g2p.encryption.provider"].create(
            {"name": "Test Provider with Key", "type": "jwcrypto"}
        )
        cls.provider_with_key.generate_and_store_jwcrypto_key()

    def test_get_jwk_key(self):
        self.assertEqual(self.provider.jwcrypto_key, False)
        with self.assertRaises(ValueError):
            self.provider._get_jwk_key()

        expected_keys = ["kty", "kid", "n", "e", "d", "p", "q", "dp", "dq", "qi"]
        self.assertTrue(all(elem in expected_keys for elem in self.provider_with_key._get_jwk_key().keys()))

    def test_encrypt_data_jwcrypto(self):
        with self.assertRaises(NotImplementedError):
            self.provide_no_type.encrypt_data(b"test")

        with patch.object(type(self.provider), "encrypt_data_jwcrypto", return_value=None) as encrypt_data_jwcrypto:
            result = self.provider.encrypt_data(b"test")
            encrypt_data_jwcrypto.assert_called_once()

        result_with_key = self.provider_with_key.encrypt_data(b"test")

        self.assertIsNone(result)
        self.assertIsNotNone(result_with_key)
        self.assertIsInstance(result_with_key, bytes)

    def test_decrypt_data_jwcrypto(self):
        with self.assertRaises(NotImplementedError):
            self.provide_no_type.decrypt_data(b"test")

        with patch.object(type(self.provider), "decrypt_data_jwcrypto", return_value=None) as decrypt_data_jwcrypto:
            self.provider.decrypt_data(b"test")
            decrypt_data_jwcrypto.assert_called_once()

        data = "test"
        encoded_data = data.encode("utf-8")

        encrypted_data = self.provider_with_key.encrypt_data(encoded_data)
        decrypted_data = self.provider_with_key.decrypt_data(encrypted_data)

        self.assertEqual(decrypted_data, encoded_data)

    def test_jwt_sign_jwcrypto(self):
        with self.assertRaises(NotImplementedError):
            self.provide_no_type.jwt_sign({})

        with patch.object(type(self.provider), "jwt_sign_jwcrypto", return_value=None) as jwt_sign_jwcrypto:
            self.provider.jwt_sign({})
            jwt_sign_jwcrypto.assert_called_once()

        data = {"test": "test"}
        result = self.provider_with_key.jwt_sign(data)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)

    def test_jwt_verify_jwcrypto(self):
        with self.assertRaises(NotImplementedError):
            self.provide_no_type.jwt_verify("test")

        with patch.object(type(self.provider), "jwt_verify_jwcrypto", return_value=None) as jwt_verify_jwcrypto:
            self.provider.jwt_verify("test")
            jwt_verify_jwcrypto.assert_called_once()

        data = {"test": "test"}
        token = self.provider_with_key.jwt_sign(data)
        verified, received_jwt = self.provider_with_key.jwt_verify(token)

        self.assertTrue(verified)
        self.assertIsNotNone(received_jwt)

    def test_get_jwks_jwcrypto(self):
        with self.assertRaises(NotImplementedError):
            self.provide_no_type.get_jwks()

        with patch.object(type(self.provider), "get_jwks_jwcrypto", return_value=None) as get_jwks_jwcrypto:
            self.provider.get_jwks()
            get_jwks_jwcrypto.assert_called_once()

        jwks = self.provider_with_key.get_jwks()

        self.assertIsNotNone(jwks)
        self.assertTrue("keys" in jwks)
        self.assertIsInstance(jwks["keys"], list)
        self.assertEqual(len(jwks["keys"]), 1)
        self.assertIsInstance(jwks["keys"][0], dict)

        expected_keys = ["kty", "kid", "n", "e", "d", "p", "q", "dp", "dq", "qi"]
        self.assertTrue(all(elem in expected_keys for elem in jwks["keys"][0].keys()))

    def test_generate_and_store_jwcrypto_key(self):
        with self.assertRaisesRegex(ValueError, "Unsupported key type. Currently, only 'RSA' is supported."):
            self.provider.generate_and_store_jwcrypto_key(key_type="DSA")

        self.assertIn(self.provider.jwcrypto_key, [False, None])

        self.provider.generate_and_store_jwcrypto_key()

        expected_keys = ["kty", "kid", "n", "e", "d", "p", "q", "dp", "dq", "qi"]

        self.assertIsNotNone(self.provider.jwcrypto_key)
        self.assertTrue(all(elem in expected_keys for elem in self.provider_with_key._get_jwk_key().keys()))
