# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
import uuid
from functools import partial

import jwt  # pylint: disable=missing-manifest-dependency
from jwt import PyJWKClient  # pylint: disable=missing-manifest-dependency
from werkzeug.exceptions import InternalServerError

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError

from ..exceptions import (
    AmbiguousJwtValidator,
    JwtValidatorNotFound,
    UnauthorizedInvalidToken,
    UnauthorizedPartnerNotFound,
)

_logger = logging.getLogger(__name__)


class AuthJWTValidator(models.Model):
    _name = "spp.auth.jwt.validator"
    _description = "JWT Validator Configuration"

    name = fields.Char(required=True)
    signature_type = fields.Selection(
        [("secret", "Secret"), ("public_key", "Public key")], required=True
    )
    secret_key = fields.Char()
    secret_algorithm = fields.Selection(
        [
            ("HS256", "HS256 - HMAC using SHA-256 hash algorithm"),
            ("HS384", "HS384 - HMAC using SHA-384 hash algorithm"),
            ("HS512", "HS512 - HMAC using SHA-512 hash algorithm"),
        ],
        default="HS256",
    )
    public_key_jwk_uri = fields.Char()
    public_key = fields.Text()
    public_key_algorithm = fields.Selection(
        [
            ("ES256", "ES256 - ECDSA using SHA-256"),
            ("ES256K", "ES256K - ECDSA with secp256k1 curve using SHA-256"),
            ("ES384", "ES384 - ECDSA using SHA-384"),
            ("ES512", "ES512 - ECDSA using SHA-512"),
            ("RS256", "RS256 - RSASSA-PKCS1-v1_5 using SHA-256"),
            ("RS384", "RS384 - RSASSA-PKCS1-v1_5 using SHA-384"),
            ("RS512", "RS512 - RSASSA-PKCS1-v1_5 using SHA-512"),
            ("PS256", "PS256 - RSASSA-PSS using SHA-256 and MGF1 padding with SHA-256"),
            ("PS384", "PS384 - RSASSA-PSS using SHA-384 and MGF1 padding with SHA-384"),
            ("PS512", "PS512 - RSASSA-PSS using SHA-512 and MGF1 padding with SHA-512"),
        ],
        default="RS256",
    )
    audience = fields.Char(
        required=True, help="Comma separated list of audiences, to validate aud."
    )
    issuer = fields.Char(required=True, help="To validate iss.")

    # JWT Decoder Options
    # TODO: default to True
    jwt_opt_verify_exp = fields.Boolean("Verify Token Expiration", default=False)
    jwt_opt_verify_sig = fields.Boolean("Verify Token Signature", default=True)

    # User Fields
    default_user_id = fields.Many2one("res.users", required=True)
    partner_id_strategy = fields.Selection(
        [("email", "From email claim")], default="email", required=True
    )

    _sql_constraints = [
        ("name_uniq", "unique(name)", "JWT validator names must be unique !"),
    ]

    @api.constrains("name")
    def _check_name(self):
        for rec in self:
            if not rec.name.isidentifier():
                raise ValidationError(
                    _("Name %r is not a valid python identifier.") % (rec.name,)
                )

    @api.model
    def _get_validator_by_name_domain(self, validator_name):
        if validator_name:
            return [("name", "=", validator_name)]
        return []

    @api.model
    def _get_validator_by_name(self, validator_name):
        domain = self._get_validator_by_name_domain(validator_name)
        validator = self.search(domain)
        if not validator:
            _logger.error("JWT validator not found for name %r", validator_name)
            raise JwtValidatorNotFound()
        if len(validator) != 1:
            _logger.error(
                "More than one JWT validator found for name %r", validator_name
            )
            raise AmbiguousJwtValidator()
        return validator

    @tools.ormcache("self.public_key_jwk_uri", "self.public_key", "kid")
    def _get_key(self, kid):
        retval = self.public_key
        if self.public_key_jwk_uri:
            jwks_client = PyJWKClient(self.public_key_jwk_uri, cache_keys=False)
            retval = jwks_client.get_signing_key(kid).key
        return retval

    # OpenSPP: Customized for the OpenG2P Rest API
    def _decode(self, token):
        """Validate and decode a JWT token, return the payload."""
        if self.signature_type == "secret":
            key = self.secret_key
            algorithm = self.secret_algorithm
        else:
            try:
                header = jwt.get_unverified_header(token)
            except Exception as e:
                _logger.info("Invalid token: %s", e)
                raise UnauthorizedInvalidToken()  # noqa: B904
            key = self._get_key(header.get("kid"))
            algorithm = self.public_key_algorithm
        try:
            payload = jwt.decode(
                token,
                key=key,
                algorithms=[algorithm],
                options=dict(
                    require=["exp", "aud", "iss"],
                    verify_exp=self.jwt_opt_verify_exp,
                    verify_aud=True,
                    verify_iss=True,
                    verify_signature=self.jwt_opt_verify_sig,
                ),
                audience=self.audience.split(","),
                issuer=self.issuer,
            )
        except Exception as e:
            _logger.info("Invalid token: %s", e)
            raise UnauthorizedInvalidToken()  # noqa: B904
        return payload

    # OpenSPP: Customized for the OpenG2P Rest API
    def _get_and_check_uid_partner_id(self, payload):
        """Get the UID and partner_id from res.users.
        If payload have email then search for it from res.users.
        If found, get the uid and partner_id.
        Otherwise, use the default_user_id for the uid and partner_id
        :param: payload
        :return: uid, partnerid
        """
        # override for additional strategies
        uid = self.default_user_id and self.default_user_id.id or None
        partner_id = (
            self.default_user_id
            and self.default_user_id.partner_id
            and self.default_user_id.partner_id.id
            or None
        )
        # Get the email in the payload
        if self.partner_id_strategy == "email":
            email = payload.get("email")
            if email:
                user = self.env["res.users"].search([("email", "=", email)])
                if user:
                    uid = user[0].id
                    partner_id = user[0].partner_id and user[0].partner_id.id or None

        _logger.info("JWT _get_and_check_uid_partner_id UID: %s" % uid)
        _logger.info("JWT _get_and_check_uid_partner_id Partner ID: %s" % partner_id)

        if not uid:
            _logger.error("JWT _get_and_check_uid_partner_id did not get a user id")
            raise InternalServerError()
        if not partner_id:
            _logger.error("JWT _get_and_check_uid_partner_id did not get a partner id")
            raise UnauthorizedPartnerNotFound()
        return uid, partner_id

    def _register_hook(self):
        res = super()._register_hook()
        self.search([])._register_auth_method()
        return res

    def _register_auth_method(self):
        IrHttp = self.env["ir.http"]
        for rec in self:
            setattr(
                IrHttp.__class__,
                f"_auth_method_jwt_{rec.name}",
                partial(IrHttp.__class__._auth_method_jwt, validator_name=rec.name),
            )
            setattr(
                IrHttp.__class__,
                f"_auth_method_public_or_jwt_{rec.name}",
                partial(
                    IrHttp.__class__._auth_method_public_or_jwt, validator_name=rec.name
                ),
            )

    def _unregister_auth_method(self):
        IrHttp = self.env["ir.http"]
        for rec in self:
            try:
                delattr(IrHttp.__class__, f"_auth_method_jwt_{rec.name}")
                delattr(IrHttp.__class__, f"_auth_method_public_or_jwt_{rec.name}")
            except AttributeError:
                _logger.debug("JWT AttributeError")

    @api.model_create_multi
    def create(self, vals):
        rec = super().create(vals)
        rec._register_auth_method()
        return rec

    def write(self, vals):
        if "name" in vals:
            self._unregister_auth_method()
        res = super().write(vals)
        self._register_auth_method()
        return res

    def unlink(self):
        self._unregister_auth_method()
        return super().unlink()

    def copy(self, default=None):
        name = f"{self.name}_{uuid.uuid4().hex}"
        if default:
            default.update({"name": name})
        else:
            default = {"name": name}

        self.ensure_one()
        new = super().copy(default)

        return new
