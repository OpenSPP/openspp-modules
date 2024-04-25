import json
import uuid

from jwcrypto import jwe, jwk, jwt
from jwcrypto.common import json_decode, json_encode
from jwcrypto.jws import InvalidJWSSignature

from odoo import fields, models


class JWCryptoEncryptionProvider(models.Model):
    _inherit = "g2p.encryption.provider"

    type = fields.Selection(selection_add=[("jwcrypto", "JWCrypto")])

    jwcrypto_key = fields.Char(help="JWK key in JSON format for encryption, decryption, signing, and verification")

    def _get_jwk_key(self):
        self.ensure_one()
        if not self.jwcrypto_key:
            raise ValueError("JWCrypto key is not set.")
        return jwk.JWK.from_json(self.jwcrypto_key)

    def encrypt_data_jwcrypto(self, data: bytes, **kwargs) -> bytes:
        self.ensure_one()
        key = self._get_jwk_key()
        enc = jwe.JWE(data, json_encode({"alg": "RSA-OAEP", "enc": "A256GCM"}))
        enc.add_recipient(key)
        return enc.serialize(compact=True).encode("utf-8")

    def decrypt_data_jwcrypto(self, data: bytes, **kwargs) -> bytes:
        self.ensure_one()
        key = self._get_jwk_key()
        enc = jwe.JWE()
        enc.deserialize(data.decode("utf-8"), key=key)
        return enc.payload

    def jwt_sign_jwcrypto(self, data, **kwargs) -> str:
        self.ensure_one()
        key = self._get_jwk_key()
        token = jwt.JWT(header={"alg": "RS256"}, claims=data)
        token.make_signed_token(key)
        return token.serialize()

    def jwt_verify_jwcrypto(self, token: str, **kwargs):
        self.ensure_one()
        key = self._get_jwk_key()
        try:
            received_jwt = jwt.JWT(key=key, jwt=token)
            verified = True
        except InvalidJWSSignature:
            received_jwt = None
            verified = False
        return verified, received_jwt

    def get_jwks_jwcrypto(self, **kwargs):
        self.ensure_one()
        key = self._get_jwk_key()
        public_key = key.export_public()
        jwks = {"keys": [json_decode(public_key)]}
        return jwks

    def generate_and_store_jwcrypto_key(self, key_type="RSA", size=2048):
        """
        Generates a new JWK (JSON Web Key) for the current record and stores it in the `jwcrypto_key` field.
        :param key_type: The type of key to generate, e.g., 'RSA'.
        :param size: The size of the key (applies to RSA keys).
        :return: None
        """
        if key_type != "RSA":
            raise ValueError("Unsupported key type. Currently, only 'RSA' is supported.")

        key = jwk.JWK.generate(kty=key_type, size=size)

        kid = str(uuid.uuid4())

        key_export = key.export()

        export_data = json.loads(key_export)
        export_data["kid"] = kid

        key_export = json.dumps(export_data)

        # Assuming this method is called on a specific record, not on the model class itself
        self.jwcrypto_key = key_export
