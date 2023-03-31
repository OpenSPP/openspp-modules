import jwt

from odoo import fields
from odoo.tests import TransactionCase

from ..exceptions import UnauthorizedInvalidToken

PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCQpS6pKR48+HBQpuPBYF4dqhCm
If0J0OSAjpLmNu+jk0UeLpcJni8dj1ipuGuztgeTejXj6GrY7Q1VPn0YIzwlOEnx
yQPwiuJT5ykoUebOlfzhGdvsmqux3g5yok6KbzduksDUTbVLknoZXMVefuuCbVZ7
VowD2nQBE3VL/iOxUQIDAQAB
-----END PUBLIC KEY-----"""
PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIICWwIBAAKBgQCQpS6pKR48+HBQpuPBYF4dqhCmIf0J0OSAjpLmNu+jk0UeLpcJ
ni8dj1ipuGuztgeTejXj6GrY7Q1VPn0YIzwlOEnxyQPwiuJT5ykoUebOlfzhGdvs
mqux3g5yok6KbzduksDUTbVLknoZXMVefuuCbVZ7VowD2nQBE3VL/iOxUQIDAQAB
AoGAb++03WoZoXtth6yvYq4OB4zdl4OEC72hp68uFYR8DS1h9sp9Tg8hTRHqvmUe
zBNZZ5LS842gakGA6PAT5MMXvlgL/zD6kV3vz2y7bF/YdfzywCkat1IzHDi2vX42
ZPpSrTj1smhzI1PSVi8BFBk0ZibnHxFbXGCbcrI/8tNUrmUCQQDGIPCQFHRqjp3k
X5GW06nO/HRSRtznc/CTh8QJomKAddGwFRMBtGYXgE1ndHM0F+BNeg8W6moFuJ0b
am5W/vurAkEAuuUFsyO3QvkS+u8jMcpffTodFBbxyIQ9TUb5mWKADOHZZeoXXjzf
kd+axxGJIT3t5Ij17Mmf8uhT8brLi7Jq8wJARTZQkyRyHp8/jP3NsDC0yzfpsqxK
kxgvXHo7A1qUqmd+HtLd1uScHW2WnKNTc0k79BTFnK2659C8IU2mygE9DQJAUzyU
4UfS4t0Tevbuccpz5M3xDXV6kZdzxesKVynrZdFghWdQqQPrfohb4rUIoel2/gWR
obfaqNCYMlzDMqBvyQJAPATaz645qoTNqjBvRYecrrM719bS7i39F/UGRuaUkBhO
HZMw9Db9nfTJ+NjBMHjUOKva6K32KuY9orwVzk/O+Q==
-----END RSA PRIVATE KEY-----"""
WRONG_PRV_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIICXgIBAAKBgQDhs5MSL2s5uv5+PcleAKgCR/H1eZgsIabHf3bXqC25vmjH8rFp
PfLPFw5sGHQm6xk08rx/L3h9gLX8ULFEiM9gsTFS4RICUI1Qqk+Q+33s63fRivtL
x7N+FOkt82g1loBRlM0BPBw1mxamx10TS5y8K9IeMeAekN0AndmdZhV4iwIDAQAB
AoGAUmURGsFu3otyXrnFqmiI7RRAs4GpWOsMDKZuxznhP37Ql7X0qFvyKUHchP/E
X3TSJe87ex7kWMTFKxB2NnPPaGiQvmNirC+DoD4lO1wIb97utNidAoDD7J0hYos3
Rm9s3pJ5GmUJv4nHT7ABIC/1Vw+roZGBT223Y9zOPvcelHkCQQDpDSzulauuKD1t
EyDwVlvNTE0ugcrG2kl09bhy+NEcCeDNiXBso4aHPxRXCreakb8grTiosgH+I2wx
0mnGw5w/AkEA9+0eOyZCuuvmKYAA4Jo4Mi8HbyBe7Qb8vNHlcJRauRvHUTEWhzOO
GBoyU7jqp58GMSd5CQw0JSsiP/FKUDgAtQJBAJEq8t0fABT43eJusuricEa+i6k3
kg8x8+XWFfIQCXmUsaJ2RUB20Bq48TuS4nF27f41yIBUeadLe17BecAlItMCQQCo
3oKr6Uikhw9zjvOKCKFkVTIsGBFwQ0Uc2577CqGs2eXuQJBGsPAFLLrA2gBDAgc2
rds8NWrDMlkW0qQ6dZrNAkEAoZ1Jk7drwIgxcgoC2lUzYRMkvEaq+cOmMr0QB41F
xzCGs82TYWm5k4RzZ63em2zFeTSbF5JXtuCGT3rkyFsM5Q==
-----END RSA PRIVATE KEY-----"""


class TestAuthJwtValidator(TransactionCase):
    def setUp(self):
        super().setUp()
        self.jwt_validator = self.env["spp.auth.jwt.validator"].create(
            {
                "name": "valid_name",
                "signature_type": "public_key",
                "public_key_algorithm": "RS256",
                "public_key": PUBLIC_KEY,
                "audience": "Odoo",
                "issuer": "OpenSPP",
                "default_user_id": self.env.ref("base.user_admin").id,
            }
        )

    def generate_bearer_token(self, prv_key, issuer, audience, algorithm=None):
        if not algorithm:
            algorithm = "RS256"
        now = fields.Datetime.now()
        expiry = fields.Datetime.add(now, hours=1)
        data = {
            "exp": expiry,
            "iss": issuer,
            "aud": audience,
        }
        return jwt.encode(data, prv_key, algorithm=algorithm)

    def test_01_correct_token(self):
        correct_token = self.generate_bearer_token(
            prv_key=PRIVATE_KEY,
            issuer=self.jwt_validator.issuer,
            audience=self.jwt_validator.audience,
        )
        self.assertTrue(
            bool(self.jwt_validator._decode(correct_token)),
            "Correct Token must be decodable!",
        )

    def test_02_token_incorrect_key(self):
        wrong_token = self.generate_bearer_token(
            prv_key=WRONG_PRV_KEY,
            issuer=self.jwt_validator.issuer,
            audience=self.jwt_validator.audience,
        )
        with self.assertRaises(UnauthorizedInvalidToken):
            self.jwt_validator._decode(wrong_token)

    def test_03_token_incorrect_issuer(self):
        wrong_token = self.generate_bearer_token(
            prv_key=PRIVATE_KEY,
            issuer="self.jwt_validator.issuer",
            audience=self.jwt_validator.audience,
        )
        with self.assertRaises(UnauthorizedInvalidToken):
            self.jwt_validator._decode(wrong_token)

    def test_04_token_incorrect_audience(self):
        wrong_token = self.generate_bearer_token(
            prv_key=PRIVATE_KEY,
            issuer=self.jwt_validator.issuer,
            audience="self.jwt_validator.audience",
        )
        with self.assertRaises(UnauthorizedInvalidToken):
            self.jwt_validator._decode(wrong_token)
