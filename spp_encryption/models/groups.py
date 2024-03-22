from odoo import models


class SPPGroup(models.Model):
    _inherit = "res.partner"

    def my_button(self):
        my_data = {
            "sub": "1234567890",
            "name": "John Doe",
            "iat": 1516239022,
            "scope": "Test",
            "iss": "http://localhost:8080/api/v1/security",
        }

        # comes from jwt.io
        token = b"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJzY29wZSI6IlRlc3QiLCJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwODAvYXBpL3YxL3NlY3VyaXR5In0.9xUHUtQBILGmL9nFeXygBtGGUoTYXBfrZ9aoCOW85II"

        g = self.env["g2p.encryption.provider"].browse(1)

        enc_data = g.encrypt_data(data=str(my_data).encode("utf-8"))

        g.jwt_sign(data=enc_data)

        credential_request = {
            "id": ".type",
            "format": "ldp_vc",
            "scope": ".scope",
            "cryptographic_binding_methods_supported": ["did:jwk"],
            "credential_signing_alg_values_supported": ["RS256"],
            "proof_types_supported": ["jwt"],
            "credential_definition": {
                "type": ["OpenG2PRegistryVerifiableCredential", ".type"],
                "credentialSubject": {
                    "fullName": {"display": [{"name": "Name", "locale": "en"}]},
                    "gender": {"display": [{"name": "Gender", "locale": "en"}]},
                    "dateOfBirth": {"display": [{"name": "Date of Birth", "locale": "en"}]},
                    "address": {"display": [{"name": "Address", "locale": "en"}]},
                    "UIN": {"display": [{"name": "Beneficiary ID", "locale": "en"}]},
                    "nationalID": {"display": [{"name": "National ID", "locale": "en"}]},
                },
            },
            "display": [
                {
                    "name": "OpenG2P Registry Credential",
                    "locale": "en",
                    "logo": {
                        "url": (".web_base_url" + "/g2p_openid_vci/static/description/icon.png"),
                        "alt_text": "a square logo of a OpenG2P",
                    },
                    "background_color": "#12107c",
                    "text_color": "#FFFFFF",
                }
            ],
            "order": ["fullName", "gender", "dateOfBirth"],
        }

        vci_issuer = self.env["g2p.openid.vci.issuers"]

        # print(signed_data)
        print("==============")
        print(g.get_jwks())

        # ValueError: Invalid Auth Token received
        vci_issuer.issue_vc(credential_request, token)

        # raise JWTError("Error decoding token claims.")
        # vci_issuer.issue_vc(credential_request, enc_data)

        # jose.exceptions.JWTError: Invalid claims string: Expecting value: line 1 column 1 (char 0)
        # vci_issuer.issue_vc(credential_request, signed_data)
