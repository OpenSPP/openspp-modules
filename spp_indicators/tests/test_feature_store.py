from __future__ import annotations

from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install", "spp_indicators")
class TestFeatureStore(TransactionCase):
    def setUp(self):
        super().setUp()
        self.company = self.env.company
        self.Feature = self.env["openspp.indicator.value"].sudo()
        self.Definition = self.env["openspp.indicator.definition"].sudo()
        self.Resolver = self.env["openspp.indicator.resolver"].sudo()
        self.metric_name = "test.feature.metric"
        self.period_key = "2025-09"

        # Ensure a clean definition exists for our metric
        existing = self.Definition.search(
            [
                ("name", "=", self.metric_name),
                ("company_id", "=", self.company.id),
            ],
            limit=1,
        )
        if existing:
            existing.unlink()
        self.Definition.create(
            {
                "name": self.metric_name,
                "subject_model": "res.partner",
                "value_type": "number",
                "period_granularity": "month",
                "default_ttl_seconds": 0,
                "company_id": self.company.id,
            }
        )

        self.partner = self.env["res.partner"].create(
            {
                "name": "Feature Store Tester",
                "is_registrant": True,
                "ref": "FS-001",
            }
        )

    def test_upsert_and_read_values(self):
        """Upsert should insert then update rows while preserving latest value."""
        result = self.Feature.upsert_values(
            [
                {
                    "metric": self.metric_name,
                    "provider": "unit-test",
                    "subject_model": "res.partner",
                    "subject_id": self.partner.id,
                    "period_key": self.period_key,
                    "value_json": 10,
                    "value_type": "number",
                    "source": "unit-test",
                }
            ]
        )
        self.assertEqual(result["inserted"], 1)
        self.assertEqual(result["updated"], 0)

        # Update with a fresh value and ensure it overwrites correctly
        result_update = self.Feature.upsert_values(
            [
                {
                    "metric": self.metric_name,
                    "provider": "unit-test",
                    "subject_model": "res.partner",
                    "subject_id": self.partner.id,
                    "period_key": self.period_key,
                    "value_json": 14,
                    "value_type": "number",
                    "source": "unit-test",
                }
            ]
        )
        self.assertEqual(result_update["inserted"], 0)
        self.assertEqual(result_update["updated"], 1)

        rows = self.Feature.read_values(
            self.metric_name,
            "res.partner",
            [self.partner.id],
            self.period_key,
            provider="unit-test",
        )
        self.assertIn(self.partner.id, rows)
        self.assertEqual(rows[self.partner.id]["value"], 14)

    def test_invalidate_marks_expired(self):
        """Invalidating should mark cached values as expired without removing them."""
        self.Feature.upsert_values(
            [
                {
                    "metric": self.metric_name,
                    "provider": "refresh-test",
                    "subject_model": "res.partner",
                    "subject_id": self.partner.id,
                    "period_key": self.period_key,
                    "value_json": 3,
                    "value_type": "number",
                    "source": "unit-test",
                }
            ]
        )

        self.Feature.invalidate(
            self.metric_name,
            "res.partner",
            self.period_key,
            [self.partner.id],
            provider="refresh-test",
        )

        rows = self.Feature.read_values(
            self.metric_name,
            "res.partner",
            [self.partner.id],
            self.period_key,
            provider="refresh-test",
        )
        self.assertIsNotNone(rows[self.partner.id]["expires_at"])

    def test_resolver_map_subjects_optional_vs_required(self):
        other = self.env["res.partner"].create({"name": "No Ref Partner", "is_registrant": True})

        mapped_optional, unmapped_optional = self.Resolver.map_subjects_to_external(
            "res.partner",
            [self.partner.id, other.id],
            ["ref"],
            required=False,
        )
        self.assertEqual(mapped_optional[self.partner.id], "FS-001")
        self.assertTrue(mapped_optional[other.id].startswith("odoo:"))
        self.assertFalse(unmapped_optional)

        mapped_required, unmapped_required = self.Resolver.map_subjects_to_external(
            "res.partner",
            [self.partner.id, other.id],
            ["ref"],
            required=True,
        )
        self.assertEqual(mapped_required[self.partner.id], "FS-001")
        self.assertIn(other.id, unmapped_required)

    def test_resolver_resolve_external_ids(self):
        partner_extra = self.env["res.partner"].create(
            {
                "name": "Resolver Target",
                "is_registrant": True,
                "ref": "FS-XYZ",
            }
        )

        entries = [
            {"index": 0, "external_id": "FS-001"},
            {"index": 1, "external_id": "FS-XYZ"},
            {"index": 2, "external_id": "MISSING"},
        ]

        mapped, errors = self.Resolver.resolve_external_ids(
            "res.partner",
            entries,
            ["ref"],
            required=True,
        )

        self.assertEqual(mapped[0], self.partner.id)
        self.assertEqual(mapped[1], partner_extra.id)
        missing_indices = {err["index"] for err in errors}
        self.assertIn(2, missing_indices)
        self.assertTrue(all(err["code"] == "mapping_missing" for err in errors))


@tagged("post_install", "-at_install", "spp_indicators")
class TestFeatureStoreTTL(TransactionCase):
    """Ensure TTL resolution logic behaves as expected without providers."""

    def setUp(self):
        super().setUp()
        self.metrics = self.env["openspp.indicator"].sudo()
        self.Feature = self.env["openspp.indicator.value"].sudo()
        self.metric = "test.ttl.metric"
        self.period_key = "rolling_30d"
        self.partner = self.env["res.partner"].create({"name": "TTL Subject", "is_registrant": True})
        self.env["openspp.indicator.definition"].sudo().create(
            {
                "name": self.metric,
                "subject_model": "res.partner",
                "value_type": "number",
                "period_granularity": "rolling",
                "default_ttl_seconds": 3600,
                "company_id": self.env.company.id,
            }
        )

    def test_default_ttl_applied_on_invalidate(self):
        """Rows missing an explicit expires_at should get one after evaluation fallback."""
        self.Feature.upsert_values(
            [
                {
                    "metric": self.metric,
                    "provider": "",
                    "subject_model": "res.partner",
                    "subject_id": self.partner.id,
                    "period_key": self.period_key,
                    "value_json": 5,
                    "value_type": "number",
                    "source": "unit-test",
                }
            ]
        )

        values, stats = self.metrics.evaluate(
            self.metric,
            "res.partner",
            [self.partner.id],
            self.period_key,
            mode="cache_only",
        )
        self.assertEqual(values.get(self.partner.id), 5)
        self.assertEqual(stats["cache_hits"], 1)

        # Trigger invalidate and backdate expiry slightly so fallback treats it as stale
        self.Feature.invalidate(self.metric, "res.partner", self.period_key, [self.partner.id])
        self.env.cr.execute(
            """
            UPDATE openspp_indicator_value
            SET expires_at = expires_at - interval '5 seconds'
            WHERE metric = %s AND subject_id = %s AND period_key = %s
            """,
            (self.metric, self.partner.id, self.period_key),
        )
        rows = self.Feature.read_values(self.metric, "res.partner", [self.partner.id], self.period_key)
        self.assertIsNotNone(rows[self.partner.id]["expires_at"])

        # Cache-only ignores expiry flags by design (returns stale value).
        stale_values, stale_stats = self.metrics.evaluate(
            self.metric,
            "res.partner",
            [self.partner.id],
            self.period_key,
            mode="cache_only",
        )
        self.assertEqual(stale_values[self.partner.id], 5)
        self.assertEqual(stale_stats["cache_hits"], 1)

        # Fallback mode should respect the expiry flag and treat the row as a miss.
        values_after, stats_after = self.metrics.evaluate(
            self.metric,
            "res.partner",
            [self.partner.id],
            self.period_key,
            mode="fallback",
        )
        self.assertNotIn(self.partner.id, values_after)
        self.assertEqual(stats_after["misses"], 1)

        # Reinsert with explicit expires_at and ensure evaluate returns value again
        self.Feature.upsert_values(
            [
                {
                    "metric": self.metric,
                    "provider": "",
                    "subject_model": "res.partner",
                    "subject_id": self.partner.id,
                    "period_key": self.period_key,
                    "value_json": 9,
                    "value_type": "number",
                    "expires_at": fields.Datetime.now() + timedelta(hours=2),
                    "source": "unit-test",
                }
            ]
        )
        fresh_values, _ = self.metrics.evaluate(
            self.metric,
            "res.partner",
            [self.partner.id],
            self.period_key,
            mode="cache_only",
        )
        self.assertEqual(fresh_values[self.partner.id], 9)
