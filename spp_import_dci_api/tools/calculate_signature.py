import os

import jwt  # pylint: disable=missing-manifest-dependency

JWT_ALGORITHM = "RS256"

dir_path = os.path.dirname(os.path.realpath(__file__))


with open(f"{dir_path}/private_key.pem") as privatefile:
    privkey = privatefile.read()


def calculate_signature(header, payload):
    return jwt.encode(headers=header, payload=payload, key=privkey, algorithm=JWT_ALGORITHM)
