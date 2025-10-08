from __future__ import annotations

from typing import Any

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install", "spp_indicators")
class TestMetricsServiceExtended(TransactionCase):
    def setUp(self):
        super().setUp()
        self.metrics = self.env["openspp.indicator"].sudo()
        self.Feature = self.env["openspp.indicator.value"].sudo()
        self.Registry = self.env["openspp.indicator.registry"].sudo()
        self.Def = self.env["openspp.indicator.definition"].sudo()
        self.partner = self.env["res.partner"].create({"name": "SvcSubj", "is_registrant": True})

    def test_any_provider_fallback_reads_cached_value(self):
        metric = "test.service.anyprov"
        period = "2025-09"
        self.Def.create(
            {
                "name": metric,
                "subject_model": "res.partner",
                "value_type": "number",
                "period_granularity": "month",
                "company_id": self.env.company.id,
            }
        )
        # Seed cache under provider 'push' only
        self.Feature.upsert_values(
            [
                {
                    "metric": metric,
                    "provider": "push",
                    "subject_model": "res.partner",
                    "subject_id": self.partner.id,
                    "period_key": period,
                    "value_json": 77,
                    "value_type": "number",
                    "source": "unit-test",
                    "fetched_at": fields.Datetime.now(),
                }
            ]
        )
        # Without a runtime registry provider, evaluate should still hit cache via any-provider fallback
        values, stats = self.metrics.evaluate(metric, "res.partner", [self.partner.id], period, mode="cache_only")
        self.assertEqual(values.get(self.partner.id), 77)
        self.assertEqual(stats["cache_hits"], 1)

    def test_provider_error_does_not_crash(self):
        metric = "test.service.error"
        period = "2025-09"
        self.Def.create(
            {
                "name": metric,
                "subject_model": "res.partner",
                "value_type": "number",
                "period_granularity": "month",
                "company_id": self.env.company.id,
            }
        )

        class Boom:
            def compute_batch(self, env, ctx: dict[str, Any], subject_ids: list[int]):
                raise RuntimeError("kaboom")

        self.Registry.register(metric, Boom(), return_type="number", subject_model="res.partner")
        values, stats = self.metrics.evaluate(metric, "res.partner", [self.partner.id], period, mode="fallback")
        # No crash, no values, and fresh_fetches stays 0
        self.assertFalse(values)
        self.assertEqual(stats["fresh_fetches"], 0)
