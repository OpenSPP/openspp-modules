from __future__ import annotations

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install", "spp_indicators")
class TestParamsHashNegative(HttpCase):
    def setUp(self):
        super().setUp()
        self.Def = self.env["openspp.indicator.definition"].sudo()
        self.Cred = self.env["openspp.indicator.api_credential"].sudo()
        self.Metrics = self.env["openspp.indicator"].sudo()
        self.Feature = self.env["openspp.indicator.value"].sudo()
        self.metric = "test.params.neg"
        self.period = "2025-09"
        self.partner = self.env["res.partner"].create({"name": "Params Neg", "is_registrant": True})
        self.Def.create(
            {
                "name": self.metric,
                "subject_model": "res.partner",
                "value_type": "number",
                "period_granularity": "month",
                "company_id": self.env.company.id,
            }
        )
        self.Cred.create(
            {
                "name": "Params Token",
                "token_plain": "params-1",
                "allowed_metric_pattern": "test.params.*",
                "company_id": self.env.company.id,
            }
        )

    def _post(self, payload, token):
        import json

        headers = {"Content-Type": "application/json", "X-Api-Key": token}
        return self.url_open("/api/indicators/push", json.dumps(payload), headers=headers)

    def test_push_with_params_then_evaluate_without_params_is_miss(self):
        payload = {
            "metric": self.metric,
            "period_key": self.period,
            "params": {"program": "EPI"},
            "items": [{"subject_id": self.partner.id, "value": 9}],
        }
        resp = self._post(payload, "params-1")
        self.assertEqual(resp.status_code, 200)
        # Evaluate w/o params should miss (different cache key)
        values, stats = self.Metrics.evaluate(
            self.metric, "res.partner", [self.partner.id], self.period, mode="cache_only", params={}
        )
        self.assertFalse(values)
        self.assertEqual(stats["cache_hits"], 0)
        # Evaluate with matching params should hit
        values2, stats2 = self.Metrics.evaluate(
            self.metric,
            "res.partner",
            [self.partner.id],
            self.period,
            mode="cache_only",
            params={"program": "EPI"},
        )
        self.assertEqual(values2.get(self.partner.id), 9)
        self.assertEqual(stats2["cache_hits"], 1)

    def test_push_without_params_then_evaluate_with_params_is_miss(self):
        payload = {
            "metric": self.metric,
            "period_key": self.period,
            "items": [{"subject_id": self.partner.id, "value": 5}],
        }
        resp = self._post(payload, "params-1")
        self.assertEqual(resp.status_code, 200)
        # Evaluate with params should miss
        values, stats = self.Metrics.evaluate(
            self.metric,
            "res.partner",
            [self.partner.id],
            self.period,
            mode="cache_only",
            params={"program": "EPI"},
        )
        self.assertFalse(values)
        self.assertEqual(stats["cache_hits"], 0)
        # Evaluate without params should hit
        values2, stats2 = self.Metrics.evaluate(
            self.metric, "res.partner", [self.partner.id], self.period, mode="cache_only", params={}
        )
        self.assertEqual(values2.get(self.partner.id), 5)
        self.assertEqual(stats2["cache_hits"], 1)
