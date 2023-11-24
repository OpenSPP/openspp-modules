import calendar
import uuid
from datetime import datetime, timedelta

from odoo import api, fields, models

from ..tools import calculate_signature


class ClientCredential(models.Model):
    _name = "spp.dci.api.client.credential"
    _description = "SPP DCI Client Credential"

    @api.model
    def _generate_client_id(self):
        client_id = str(uuid.uuid4())
        while self.search_count([("client_id", "=", client_id)]):
            client_id = str(uuid.uuid4())

        return client_id

    @api.model
    def _generate_client_secret(self):
        client_secret = str(uuid.uuid4())
        while self.search_count([("client_secret", "=", client_secret)]):
            client_secret = str(uuid.uuid4())

        return client_secret

    name = fields.Char("Client Name", required=True)
    client_id = fields.Char(required=True, readonly=True, default=_generate_client_id)
    client_secret = fields.Char(
        required=True, readonly=True, default=_generate_client_secret
    )

    _sql_constraints = [
        ("name_uniq", "unique(name)", "Client Name must be unique !"),
        ("client_id_uniq", "unique(client_id)", "Client ID must be unique !"),
        (
            "client_secret_uniq",
            "unique(client_secret)",
            "Client Secret must be unique !",
        ),
    ]

    TOKEN_EXPIRATION_MIN = 10

    @api.model
    def generate_access_token(self):
        today = datetime.today()
        expiry_datetime = today + timedelta(minutes=self.TOKEN_EXPIRATION_MIN)

        header = {"alg": "RS256", "typ": "JWT"}
        payload = {
            "iat": calendar.timegm(today.timetuple()),
            "exp": calendar.timegm(expiry_datetime.timetuple()),
            "iss": "openspp:auth-service",
        }

        return calculate_signature(header, payload)
