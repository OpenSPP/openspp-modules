from __future__ import annotations

import hashlib

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class OpensppIndicatorApiCredential(models.Model):
    _name = "openspp.indicator.api_credential"
    _description = "OpenSPP Metrics API Credential"
    _order = "name"

    STATUS_SELECTION = [("active", "Active"), ("inactive", "Inactive")]

    name = fields.Char(required=True)
    token_hash = fields.Char(string="Token Hash", required=True, readonly=True, copy=False)
    token_prefix = fields.Char(string="Token Prefix", readonly=True, copy=False)
    token_plain = fields.Char(
        string="Plain Token",
        store=False,
        copy=False,
        help="Set to rotate the API token. Value is hashed on save and never stored in cleartext.",
    )
    allowed_metric_pattern = fields.Char(
        help="Comma-separated wildcard patterns allowed for this token. Empty means all metrics."
    )
    request_limit = fields.Integer(
        default=0, help="Maximum number of requests per rolling hour. 0 disables throttling."
    )
    request_count = fields.Integer(default=0, readonly=True)
    request_window_start = fields.Datetime(readonly=True)
    status = fields.Selection(STATUS_SELECTION, default="active", required=True)
    expires_at = fields.Datetime()
    last_used_at = fields.Datetime(readonly=True)
    last_seen_ip = fields.Char(readonly=True)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True, index=True)
    notes = fields.Text()

    _sql_constraints = [
        (
            "openspp_metrics_api_cred_name_uniq",
            "unique(name, company_id)",
            "Credential names must be unique per company.",
        ),
    ]

    def write(self, vals):
        vals = dict(vals)
        token_plain = vals.pop("token_plain", None)
        if token_plain:
            vals.update(self._prepare_token_fields(token_plain))
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        prepared_vals = []
        now = fields.Datetime.now()
        for vals in vals_list:
            data = dict(vals)
            token_plain = data.pop("token_plain", None)
            if not token_plain and not data.get("token_hash"):
                raise ValidationError("Token is required when creating a credential.")
            if token_plain:
                data.update(self._prepare_token_fields(token_plain))
            elif data.get("token_hash"):
                data.setdefault("token_prefix", data["token_hash"][:6])
            data.setdefault("request_window_start", now)
            data.setdefault("company_id", self.env.company.id)
            prepared_vals.append(data)
        recs = super().create(prepared_vals)
        return recs

    def _prepare_token_fields(self, token: str):
        token = (token or "").strip()
        if not token:
            raise ValidationError("Token cannot be empty.")
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        return {
            "token_hash": token_hash,
            "token_prefix": token[:6],
            "last_used_at": False,
            "request_count": 0,
            "request_window_start": fields.Datetime.now(),
        }

    def check_active(self):
        now = fields.Datetime.now()
        for rec in self:
            if rec.status != "active":
                raise ValidationError("Credential is inactive.")
            if rec.expires_at and rec.expires_at < now:
                raise ValidationError("Credential has expired.")
        return True

    def matches_metric(self, metric: str) -> bool:
        self.ensure_one()
        patterns = [p.strip() for p in (self.allowed_metric_pattern or "").split(",") if p.strip()]
        if not patterns:
            return True
        for pattern in patterns:
            if self._pattern_match(metric, pattern):
                return True
        return False

    @staticmethod
    def _pattern_match(value: str, pattern: str) -> bool:
        from fnmatch import fnmatch

        return fnmatch(value, pattern)

    def bump_usage(self, remote_ip: str = ""):
        now = fields.Datetime.now()
        window_start = self.request_window_start or now
        if self.request_limit and self.request_limit > 0:
            delta = (now - window_start).total_seconds()
            if delta >= 3600:
                self.write(
                    {
                        "request_count": 1,
                        "request_window_start": now,
                        "last_used_at": now,
                        "last_seen_ip": remote_ip,
                    }
                )
            else:
                if self.request_count >= self.request_limit:
                    raise ValidationError("Credential has exceeded the request limit.")
                self.write(
                    {
                        "request_count": self.request_count + 1,
                        "last_used_at": now,
                        "last_seen_ip": remote_ip,
                    }
                )
        else:
            self.write({"last_used_at": now, "last_seen_ip": remote_ip})

    @api.model
    def find_by_token(self, token: str):
        if not token:
            return self.browse()
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        return self.search([("token_hash", "=", token_hash)], limit=1)
