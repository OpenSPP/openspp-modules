# Part of OpenG2P Registry. See LICENSE file for full copyright and licensing details.

from werkzeug.exceptions import InternalServerError, Unauthorized


class UnauthorizedMissingAuthorizationHeader(Unauthorized):
    pass


class UnauthorizedMalformedAuthorizationHeader(Unauthorized):
    pass


class UnauthorizedSessionMismatch(Unauthorized):
    pass


class AmbiguousJwtValidator(InternalServerError):
    pass


class JwtValidatorNotFound(InternalServerError):
    pass


class UnauthorizedInvalidToken(Unauthorized):
    pass


class UnauthorizedPartnerNotFound(Unauthorized):
    pass
