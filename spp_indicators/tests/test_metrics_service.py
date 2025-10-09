from __future__ import annotations

import hashlib
from datetime import datetime, timedelta

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install", "spp_indicators")
class TestMetricsService(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Feature = self.env["openspp.indicator.value"].sudo()
        self.metrics = self.env["openspp.indicator"].sudo()
        self.metric_name = "test.service.metric"
        self.period_key = "current"
        self.partner = self.env["res.partner"].create({"name": "Service HH", "is_registrant": True, "is_group": True})
        self.env["openspp.indicator.definition"].sudo().create(
            {
                "name": self.metric_name,
                "subject_model": "res.partner",
                "value_type": "number",
                "period_granularity": "static",
                "default_ttl_seconds": 0,
                "company_id": self.env.company.id,
            }
        )

    def _seed(self, value, expires_delta=None, provider="", params_hash=None):
        now = datetime.utcnow()
        expires = now + (expires_delta or timedelta(hours=1)) if expires_delta is not None else None
        self.Feature.upsert_values(
            [
                {
                    "metric": self.metric_name,
                    "provider": provider,
                    "subject_model": "res.partner",
                    "subject_id": self.partner.id,
                    "period_key": self.period_key,
                    "value_json": value,
                    "value_type": "number",
                    "as_of": now,
                    "fetched_at": now,
                    "expires_at": expires,
                    "source": "unit_test",
                    "params_hash": params_hash or "",
                }
            ]
        )

    def test_cache_only_hits_and_misses(self):
        self._seed(3, expires_delta=timedelta(days=1), provider="")
        values, stats = self.metrics.evaluate(
            self.metric_name, "res.partner", [self.partner.id], self.period_key, mode="cache_only"
        )
        self.assertEqual(values[self.partner.id], 3)
        self.assertEqual(stats["cache_hits"], 1)

        # Re-seed as expired and ensure fallback respects expiry (cache_only keeps stale rows)
        self._seed(3, expires_delta=timedelta(hours=-1), provider="")
        values2, stats2 = self.metrics.evaluate(
            self.metric_name,
            "res.partner",
            [self.partner.id],
            self.period_key,
            mode="fallback",
        )
        self.assertNotIn(self.partner.id, values2)
        self.assertEqual(stats2["misses"], 1)

    def test_fallback_respects_expiry(self):
        self._seed(5, expires_delta=timedelta(hours=-1), provider="")  # already expired
        values, stats = self.metrics.evaluate(
            self.metric_name, "res.partner", [self.partner.id], self.period_key, mode="fallback"
        )
        self.assertNotIn(self.partner.id, values)
        self.assertEqual(stats["misses"], 1)

    def test_read_any_provider(self):
        # seed value with provider label that differs from registry default and matching params hash
        params_hash = hashlib.sha1(b"{}").hexdigest()
        self._seed(7, expires_delta=timedelta(hours=4), provider="custom_provider", params_hash=params_hash)
        self.env["ir.config_parameter"].sudo().set_param("openspp_metrics.allow_any_provider_fallback", "1")
        values, stats = self.metrics.with_context(openspp_metrics_allow_any_provider_fallback=True).evaluate(
            self.metric_name,
            "res.partner",
            [self.partner.id],
            self.period_key,
            mode="cache_only",
            params={},
        )
        self.assertEqual(values.get(self.partner.id), 7)
        self.assertTrue(stats["cache_any_provider_used"])
