from __future__ import annotations

import io
import json
from urllib.error import HTTPError

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install", "spp_indicators")
class TestMetricsPush(HttpCase):
    def setUp(self):
        super().setUp()
        self.Definition = self.env["openspp.indicator.definition"].sudo()
        self.Credential = self.env["openspp.indicator.api_credential"].sudo()
        self.Feature = self.env["openspp.indicator.value"].sudo()
        # clean up existing demo rows for our test metrics
        self.Feature.search([("metric", "ilike", "test.push%")]).unlink()

    # Helpers ----------------------------------------------------------------
    def _ensure_definition(self, name: str, **kwargs):
        default_vals = {
            "subject_model": "res.partner",
            "value_type": "number",
            "period_granularity": "month",
            "default_ttl_seconds": 0,
        }
        default_vals.update(kwargs)
        existing = self.Definition.search([("name", "=", name), ("company_id", "=", self.env.company.id)], limit=1)
        if existing:
            existing.write({k: v for k, v in default_vals.items() if v is not None})
            return existing
        default_vals["name"] = name
        default_vals["company_id"] = self.env.company.id
        return self.Definition.create(default_vals)

    def _ensure_credential(self, name: str, token_plain: str, pattern: str):
        existing = self.Credential.search([("name", "=", name), ("company_id", "=", self.env.company.id)], limit=1)
        if existing:
            existing.write({"token_plain": token_plain, "allowed_metric_pattern": pattern, "status": "active"})
            return existing
        return self.Credential.create(
            {
                "name": name,
                "token_plain": token_plain,
                "allowed_metric_pattern": pattern,
                "status": "active",
                "company_id": self.env.company.id,
            }
        )

    def _post_json(self, url: str, payload: dict, headers=None):
        headers = headers.copy() if headers else {}
        headers.setdefault("Content-Type", "application/json")
        resp = self.url_open(url, json.dumps(payload), headers=headers)
        if resp.status_code >= 400:
            buffer = io.BytesIO(resp.content or b"")
            raise HTTPError(resp.url, resp.status_code, resp.reason, resp.headers, buffer)
        return resp.json()

    def _push(self, payload: dict, token: str):
        headers = {"X-Api-Key": token}
        return self._post_json("/api/indicators/push", payload, headers=headers)

    # Tests ------------------------------------------------------------------
    def test_push_with_external_id_mapping(self):
        metric = "test.push_ref"
        period_key = "2025-09"
        self._ensure_definition(
            metric,
            id_mapping_fields="ref",
            id_mapping_required=True,
            default_ttl_seconds=3600,
        )
        self._ensure_credential("Test Push Token", "push-token", "test.*")
        partner = self.env["res.partner"].create({"name": "Push Student", "ref": "P-001"})

        payload = {
            "metric": metric,
            "period_key": period_key,
            "params": {"program": "EPI"},
            "subject_external_id_type": "demo_ref",
            "items": [
                {"subject_external_id": partner.ref, "value": 1, "coverage": 1.0},
            ],
        }
        result = self._push(payload, token="push-token")

        self.assertTrue(result["ok"])
        self.assertEqual(result["inserted"], 1)
        self.assertEqual(result["updated"], 0)
        self.assertEqual(result["errors"], [])

        row = self.Feature.search(
            [
                ("metric", "=", metric),
                ("subject_id", "=", partner.id),
                ("period_key", "=", period_key),
            ],
            limit=1,
        )
        self.assertTrue(row, "Feature store row should be created")
        self.assertEqual(row.value_json, 1)
        self.assertEqual(row.provider, payload.get("provider", "push"))

        values, stats = (
            self.env["openspp.indicator"]
            .sudo()
            .evaluate(
                metric,
                "res.partner",
                [partner.id],
                period_key,
                mode="cache_only",
            )
        )
        self.assertEqual(values.get(partner.id), 1)
        self.assertEqual(stats["cache_hits"], 1)

    def test_push_dry_run(self):
        metric = "test.push_dry_run"
        period_key = "2025-10"
        self._ensure_definition(metric, id_mapping_fields="ref", id_mapping_required=False)
        self._ensure_credential("DryRun Token", "dry-token", "test.push_dry_run")
        partner = self.env["res.partner"].create({"name": "Dry Run", "ref": "DRY-1"})

        payload = {
            "metric": metric,
            "period_key": period_key,
            "errors_only": True,
            "items": [
                {"subject_external_id": partner.ref, "value": 42},
            ],
        }
        result = self._push(payload, token="dry-token")

        self.assertTrue(result["ok"])
        self.assertTrue(result["dry_run"])
        self.assertEqual(result["inserted"], 0)
        self.assertEqual(result["processed"], 1)

        row = self.Feature.search(
            [
                ("metric", "=", metric),
                ("subject_id", "=", partner.id),
            ],
            limit=1,
        )
        self.assertFalse(row, "Dry run should not insert rows")

    def test_push_required_mapping_error(self):
        metric = "test.push_required"
        period_key = "2025-11"
        self._ensure_definition(metric, id_mapping_fields="ref", id_mapping_required=True)
        self._ensure_credential("Required Token", "req-token", "test.push_required")

        payload = {
            "metric": metric,
            "period_key": period_key,
            "items": [
                {"subject_external_id": "UNKNOWN", "value": 7},
            ],
        }
        result = self._push(payload, token="req-token")

        self.assertTrue(result["ok"])
        self.assertEqual(result["inserted"], 0)
        self.assertGreaterEqual(len(result["errors"]), 1)
        first_error = result["errors"][0]
        self.assertEqual(first_error["code"], "mapping_missing")

        rows = self.Feature.search([("metric", "=", metric)])
        self.assertFalse(rows, "No feature rows should be stored when mapping fails")

    def test_push_unknown_metric(self):
        self._ensure_credential("Unknown Metric Token", "unknown-token", "*")
        payload = {
            "metric": "test.unknown_metric",
            "period_key": "2025-01",
            "items": [{"subject_id": 1, "value": 1}],
        }
        headers = {"X-Api-Key": "unknown-token"}
        with self.assertRaises(HTTPError) as err:
            self._post_json("/api/indicators/push", payload, headers=headers)
        self.assertEqual(err.exception.code, 404)
        body = json.loads(err.exception.read().decode("utf-8") or "{}")
        self.assertEqual(body.get("error"), "unknown_metric")
