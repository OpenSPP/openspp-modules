import contextlib
from unittest.mock import Mock, patch

import odoo
from odoo.tools import mute_logger
from odoo.tools.misc import DotDict

from ..exceptions import (  # noqa
    UnauthorizedMalformedAuthorizationHeader,
    UnauthorizedMissingAuthorizationHeader,
)
from .test_auth_jwt_validator import PRIVATE_KEY, TestAuthJwtValidator


class TestIrHttp(TestAuthJwtValidator):
    @contextlib.contextmanager
    def _mock_request(self, authorization):
        environ = {}
        if authorization:
            environ["HTTP_AUTHORIZATION"] = authorization
        request = Mock(
            context={},
            db=self.env.cr.dbname,
            uid=None,
            httprequest=Mock(environ=environ),
            session=DotDict(),
            env=self.env,
        )
        # These attributes are added upon successful auth, so make sure
        # calling hasattr on the mock when they are not yet set returns False.
        del request.jwt_payload
        del request.jwt_partner_id

        with contextlib.ExitStack() as s:
            odoo.http._request_stack.push(request)
            s.callback(odoo.http._request_stack.pop)
            yield request

    @mute_logger("odoo.addons.spp_rest_auth_jwt.models.ir_http")
    def test_06_get_bearer_token(self):
        with self._mock_request(None):
            with self.assertRaises(UnauthorizedMissingAuthorizationHeader):
                self.env["ir.http"]._get_bearer_token()
        with self._mock_request("Bearerer 12345"):
            with self.assertRaises(UnauthorizedMalformedAuthorizationHeader):
                self.env["ir.http"]._get_bearer_token()
        with self._mock_request("Bearer 12345"):
            token = self.env["ir.http"]._get_bearer_token()
            self.assertEqual(
                token, "12345", "Method should return correct bearer token!"
            )

    @patch(
        "odoo.addons.spp_rest_auth_jwt.models.auth_jwt_validator."
        "AuthJWTValidator._get_validator_by_name"
    )
    def test_07_auth_method_jwt(self, mock_func):
        admin = self.env.ref("base.user_admin")
        correct_token = self.generate_bearer_token(
            prv_key=PRIVATE_KEY,
            issuer=self.jwt_validator.issuer,
            audience=self.jwt_validator.audience,
        )
        mock_func.return_value = self.jwt_validator
        with self._mock_request(f"Bearer {correct_token}"):
            with self.assertLogs(
                "odoo.addons.spp_rest_auth_jwt.models.auth_jwt_validator"
            ) as log_catcher:
                self.env["ir.http"]._auth_method_jwt("valid_name")
                result = [
                    "INFO:odoo.addons.spp_rest_auth_jwt.models.auth_jwt_validator:"
                    f"JWT _get_and_check_uid_partner_id UID: {admin.id}",
                    "INFO:odoo.addons.spp_rest_auth_jwt.models.auth_jwt_validator:"
                    f"JWT _get_and_check_uid_partner_id Partner ID: {admin.partner_id.id}",
                ]
                self.assertListEqual(
                    log_catcher.output,
                    result,
                    "_auth_method_jwt should give us correct user & partner id",
                )

    @patch(
        "odoo.addons.spp_rest_auth_jwt.models.auth_jwt_validator.AuthJWTValidator._get_validator_by_name"
    )
    def test_08_auth_method_jwt_email_partner_id_strategy(self, mock_func):
        admin = self.env.ref("base.user_admin")
        correct_token = self.generate_bearer_token(
            prv_key=PRIVATE_KEY,
            issuer=self.jwt_validator.issuer,
            audience=self.jwt_validator.audience,
            email=admin.email,
        )
        mock_func.return_value = self.jwt_validator
        self.jwt_validator.partner_id_strategy = "email"
        with self._mock_request(f"Bearer {correct_token}"):
            with self.assertLogs(
                "odoo.addons.spp_rest_auth_jwt.models.auth_jwt_validator"
            ) as log_catcher:
                self.env["ir.http"]._auth_method_jwt("valid_name")
                result = [
                    "INFO:odoo.addons.spp_rest_auth_jwt.models.auth_jwt_validator:"
                    f"JWT _get_and_check_uid_partner_id UID: {admin.id}",
                    "INFO:odoo.addons.spp_rest_auth_jwt.models.auth_jwt_validator:"
                    f"JWT _get_and_check_uid_partner_id Partner ID: {admin.partner_id.id}",
                ]
                self.assertListEqual(
                    log_catcher.output,
                    result,
                    "_auth_method_jwt should give us correct user & partner id",
                )
