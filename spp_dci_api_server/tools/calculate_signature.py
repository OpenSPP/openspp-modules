import jwt

from odoo.tools.misc import file_open

JWT_ALGORITHM = "RS256"


with file_open("spp_dci_api_server/tools/private_key.pem") as privatefile:
    privkey = privatefile.read()

with file_open("spp_dci_api_server/tools/public_key.pub") as publicfile:
    pubkey = publicfile.read()


def calculate_signature(header, payload):
    return jwt.encode(
        headers=header, payload=payload, key=privkey, algorithm=JWT_ALGORITHM
    )


def verify_and_decode_signature(access_token):
    try:
        return True, jwt.decode(access_token, key=pubkey, algorithms=[JWT_ALGORITHM])
    except Exception as e:
        return False, str(e)
