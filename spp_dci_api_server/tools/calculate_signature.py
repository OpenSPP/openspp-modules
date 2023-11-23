import os

import jwt

JWT_ALGORITHM = "RS256"

dir_path = os.path.dirname(os.path.realpath(__file__))


with open(f"{dir_path}/private_key.pem") as privatefile:
    privkey = privatefile.read()

with open(f"{dir_path}/public_key.pub") as publicfile:
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
