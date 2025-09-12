import uuid

from ..tools.rsa_encode_decode import calculate_signature
from .common import Common


class TestRSA(Common):
    def test_01_get_private_key(self):
        self.set_parameters()

        from ..tools.rsa_encode_decode import get_private_key

        private_key = get_private_key(self.env)
        self.assertTrue(private_key is not None)

    def test_02_get_public_key(self):
        self.set_parameters()

        from ..tools.rsa_encode_decode import get_public_key

        public_key = get_public_key(self.env)
        self.assertTrue(public_key is not None)

    def test_03_calculate_signature(self):
        self.set_parameters()

        from ..tools.rsa_encode_decode import calculate_signature

        openapi_token = str(uuid.uuid4())

        token = calculate_signature(
            env=self.env,
            header=None,
            payload={
                "database": self.env.cr.dbname,
                "token": openapi_token,
            },
        )
        self.assertTrue(token is not None)

    def test_04_verify_and_decode_signature(self):
        self.set_parameters()

        from ..tools.rsa_encode_decode import verify_and_decode_signature

        openapi_token = str(uuid.uuid4())

        token = calculate_signature(
            env=self.env,
            header=None,
            payload={
                "database": self.env.cr.dbname,
                "token": openapi_token,
            },
        )
        self.assertTrue(token is not None)

        decoded = verify_and_decode_signature(
            env=self.env,
            access_token=token,
        )
        self.assertTrue(decoded is not None)
        self.assertEqual(decoded.get("database"), self.env.cr.dbname)
        self.assertEqual(decoded.get("token"), openapi_token)
