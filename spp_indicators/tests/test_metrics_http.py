from __future__ import annotations

import io
import json
from urllib.error import HTTPError

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install", "spp_indicators")
class TestMetricsHttp(HttpCase):
    def setUp(self):
        super().setUp()
        self.Definition = self.env["openspp.indicator.definition"].sudo()
        self.Credential = self.env["openspp.indicator.api_credential"].sudo()
        self.Feature = self.env["openspp.indicator.value"].sudo()
        self.Icp = self.env["ir.config_parameter"].sudo()
        self._param_backups = {}
        self.addCleanup(self._restore_params)
        self.partner = self.env["res.partner"].create({"name": "HTTP Tester", "is_registrant": True})
        self.metric = "test.http.metric"
        self.period_key = "2025-09"
        self.Definition.create(
            {
                "name": self.metric,
                "subject_model": "res.partner",
                "value_type": "number",
                "period_granularity": "month",
                "default_ttl_seconds": 0,
                "company_id": self.env.company.id,
            }
        )

    # Helpers ----------------------------------------------------------------
    def _restore_params(self):
        for key, original in self._param_backups.items():
            self.Icp.set_param(key, original if original is not None else False)

    def _set_param(self, key, value):
        if key not in self._param_backups:
            self._param_backups[key] = self.Icp.get_param(key)
        self.Icp.set_param(key, value)

    def _credential(self, token="http-token", pattern=None, status="active", **extra_vals):
        pattern = pattern or "test.http.*"
        existing = self.Credential.search(
            [("name", "=", "HTTP Token"), ("company_id", "=", self.env.company.id)], limit=1
        )
        vals = {
            "name": "HTTP Token",
            "allowed_metric_pattern": pattern,
            "token_plain": token,
            "status": status,
            "company_id": self.env.company.id,
        }
        vals.update(extra_vals)
        if existing:
            existing.write(vals)
            return existing
        return self.Credential.create(vals)

    def _post_json(self, url, payload, headers=None):
        headers = headers or {}
        headers.setdefault("Content-Type", "application/json")
        resp = self.url_open(url, json.dumps(payload), headers=headers, allow_redirects=False)
        if resp.status_code >= 400:
            buffer = io.BytesIO(resp.content or b"")
            raise HTTPError(resp.url, resp.status_code, resp.reason, resp.headers, buffer)
        try:
            return resp.json()
        except ValueError as exc:
            body = (resp.content or b"").decode("utf-8", errors="ignore")
            raise AssertionError(f"Expected JSON response, got: {resp.status_code} {body}") from exc

    def _push(self, payload, token=None):
        headers = {}
        if token:
            headers["X-Api-Key"] = token
        return self._post_json("/api/indicators/push", payload, headers=headers)

    # Tests ------------------------------------------------------------------
    def test_push_requires_token_when_enforced(self):
        self._set_param("openspp_metrics.require_api_key", "1")
        payload = {
            "metric": self.metric,
            "period_key": self.period_key,
            "items": [{"subject_id": self.partner.id, "value": 5}],
        }
        with self.assertRaises(HTTPError) as err:
            self._push(payload, token=None)
        self.assertEqual(err.exception.code, 401)
        detail = json.loads(err.exception.read().decode("utf-8") or "{}")
        self.assertEqual(detail.get("error"), "missing_token")

    def test_push_with_valid_token(self):
        self._credential(token="valid-token")
        payload = {
            "metric": self.metric,
            "period_key": self.period_key,
            "items": [{"subject_id": self.partner.id, "value": 9}],
        }
        result = self._push(payload, token="valid-token")
        self.assertTrue(result["ok"])
        self.assertEqual(result["inserted"], 1)
        row = self.Feature.search(
            [
                ("metric", "=", self.metric),
                ("subject_id", "=", self.partner.id),
                ("period_key", "=", self.period_key),
            ],
            limit=1,
        )
        self.assertTrue(row)
        self.assertEqual(row.value_json, 9)

    def test_push_rejected_when_metric_not_allowed(self):
        self._credential(token="limited-token", pattern="health.*")
        payload = {
            "metric": self.metric,
            "period_key": self.period_key,
            "items": [{"subject_id": self.partner.id, "value": 1}],
        }
        with self.assertRaises(HTTPError) as err:
            self._push(payload, token="limited-token")
        self.assertEqual(err.exception.code, 403)
        body = json.loads(err.exception.read().decode("utf-8") or "{}")
        self.assertEqual(body.get("error"), "metric_not_allowed")

    def test_invalidate_endpoint_supports_external_ids(self):
        definition = self.Definition.search([("name", "=", self.metric)], limit=1)
        definition.write({"id_mapping_fields": "ref", "id_mapping_required": False})
        self.partner.ref = "EXT-123"
        self._credential(token="invalidate-token")
        # First push a value
        self._push(
            {
                "metric": self.metric,
                "period_key": self.period_key,
                "items": [{"subject_id": self.partner.id, "value": 33}],
            },
            token="invalidate-token",
        )
        # Now invalidate via external id
        payload = {
            "metric": self.metric,
            "period_key": self.period_key,
            "subject_external_ids": ["EXT-123"],
        }
        headers = {"Content-Type": "application/json", "X-Api-Key": "invalidate-token"}
        result = self._post_json("/api/indicators/invalidate", payload, headers=headers)
        self.assertTrue(result["ok"])
        row = self.Feature.search(
            [
                ("metric", "=", self.metric),
                ("subject_id", "=", self.partner.id),
                ("period_key", "=", self.period_key),
            ],
            limit=1,
        )
        self.assertTrue(row)
        self.assertTrue(row.expires_at)

    def test_push_records_errors_for_unmapped_subjects(self):
        definition = self.Definition.search([("name", "=", self.metric)], limit=1)
        definition.write({"id_mapping_fields": "ref", "id_mapping_required": True})
        self._credential(token="error-token")
        result = self._push(
            {
                "metric": self.metric,
                "period_key": self.period_key,
                "items": [{"subject_external_id": "UNKNOWN", "value": 10}],
            },
            token="error-token",
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["inserted"], 0)
        self.assertGreater(len(result["errors"]), 0)
        logged = self.env["openspp.indicator.push.error"].sudo().search([("metric", "=", self.metric)], limit=1)
        self.assertTrue(logged)
        self.assertEqual(logged.error_code, "mapping_missing")

    def test_push_rejected_with_invalid_token(self):
        self._credential(token="correct-token")
        payload = {
            "metric": self.metric,
            "period_key": self.period_key,
            "items": [{"subject_id": self.partner.id, "value": 11}],
        }
        with self.assertRaises(HTTPError) as err:
            self._push(payload, token="wrong-token")
        self.assertEqual(err.exception.code, 401)
        detail = json.loads(err.exception.read().decode("utf-8") or "{}")
        self.assertEqual(detail.get("error"), "invalid_token")

    def test_push_rejected_when_credential_inactive(self):
        self._credential(token="inactive-token", status="inactive")
        payload = {
            "metric": self.metric,
            "period_key": self.period_key,
            "items": [{"subject_id": self.partner.id, "value": 7}],
        }
        with self.assertRaises(HTTPError) as err:
            self._push(payload, token="inactive-token")
        self.assertEqual(err.exception.code, 401)
        detail = json.loads(err.exception.read().decode("utf-8") or "{}")
        self.assertEqual(detail.get("error"), "credential_inactive")

    def test_push_rate_limited_returns429(self):
        cred = self._credential(token="limited-token")
        cred.write({"request_limit": 1})
        payload = {
            "metric": self.metric,
            "period_key": self.period_key,
            "items": [{"subject_id": self.partner.id, "value": 4}],
        }
        # first request succeeds and consumes the allowed slot
        self._push(payload, token="limited-token")
        with self.assertRaises(HTTPError) as err:
            self._push(payload, token="limited-token")
        self.assertEqual(err.exception.code, 429)
        detail = json.loads(err.exception.read().decode("utf-8") or "{}")
        self.assertEqual(detail.get("error"), "rate_limited")
