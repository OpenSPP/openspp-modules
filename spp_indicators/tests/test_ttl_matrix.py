from __future__ import annotations

from odoo import fields
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install", "spp_indicators")
class TestTTLMatrix(HttpCase):
    def setUp(self):
        super().setUp()
        self.Def = self.env["openspp.indicator.definition"].sudo()
        self.Prov = self.env["openspp.indicator.provider"].sudo()
        self.Cred = self.env["openspp.indicator.api_credential"].sudo()
        self.Feature = self.env["openspp.indicator.value"].sudo()
        self.Icp = self.env["ir.config_parameter"].sudo()
        self.metric = "test.ttl.matrix"
        self.partner = self.env["res.partner"].create({"name": "TTL Matrix", "is_registrant": True})
        self.addCleanup(self._cleanup_icp)

    def _cleanup_icp(self):
        # Clear any param we set; tests run in shared DB during suite
        self.Icp.set_param("openspp_metrics.default_ttl", False)

    def _push(self, token: str):
        payload = {
            "metric": self.metric,
            "period_key": "2025-09",
            "items": [{"subject_id": self.partner.id, "value": 1}],
        }
        headers = {"Content-Type": "application/json", "X-Api-Key": token}
        resp = self.url_open("/api/indicators/push", self._dump(payload), headers=headers)
        self.assertEqual(resp.status_code, 200)

    def _dump(self, payload):
        import json

        return json.dumps(payload)

    def _row(self):
        return self.Feature.search([("metric", "=", self.metric), ("subject_id", "=", self.partner.id)], limit=1)

    def test_ttl_prefers_provider_over_definition(self):
        # provider default_ttl=1800, definition default_ttl_seconds=3600 -> expect ~+1800
        self.Def.create(
            {
                "name": self.metric,
                "subject_model": "res.partner",
                "value_type": "number",
                "period_granularity": "month",
                "default_ttl_seconds": 3600,
                "company_id": self.env.company.id,
            }
        )
        self.Prov.create(
            {
                "name": "push",
                "metric": self.metric,
                "default_ttl": 1800,
                "company_id": self.env.company.id,
            }
        )
        self.Cred.create(
            {
                "name": "TTL Token",
                "token_plain": "ttl-provider",
                "allowed_metric_pattern": "test.ttl.*",
                "company_id": self.env.company.id,
            }
        )
        now = fields.Datetime.now()
        self._push("ttl-provider")
        row = self._row()
        self.assertTrue(row)
        self.assertIsNotNone(row.expires_at)
        delta = fields.Datetime.to_datetime(row.expires_at) - fields.Datetime.to_datetime(now)
        # Allow a small scheduling drift
        self.assertTrue(1700 <= delta.total_seconds() <= 1900)

    def test_ttl_falls_back_to_definition(self):
        # provider missing, definition default_ttl_seconds=900 -> expect ~+900
        self.Def.create(
            {
                "name": self.metric,
                "subject_model": "res.partner",
                "value_type": "number",
                "period_granularity": "month",
                "default_ttl_seconds": 900,
                "company_id": self.env.company.id,
            }
        )
        self.Cred.create(
            {
                "name": "TTL Token 2",
                "token_plain": "ttl-def",
                "allowed_metric_pattern": "test.ttl.*",
                "company_id": self.env.company.id,
            }
        )
        now = fields.Datetime.now()
        self._push("ttl-def")
        row = self._row()
        self.assertIsNotNone(row.expires_at)
        delta = fields.Datetime.to_datetime(row.expires_at) - fields.Datetime.to_datetime(now)
        self.assertTrue(800 <= delta.total_seconds() <= 1000)

    def test_ttl_falls_back_to_icp_param(self):
        # No provider, no definition TTL, ICP param wins
        self.Def.create(
            {
                "name": self.metric,
                "subject_model": "res.partner",
                "value_type": "number",
                "period_granularity": "month",
                "default_ttl_seconds": 0,
                "company_id": self.env.company.id,
            }
        )
        self.Icp.set_param("openspp_metrics.default_ttl", "300")
        self.Cred.create(
            {
                "name": "TTL Token 3",
                "token_plain": "ttl-icp",
                "allowed_metric_pattern": "test.ttl.*",
                "company_id": self.env.company.id,
            }
        )
        now = fields.Datetime.now()
        self._push("ttl-icp")
        row = self._row()
        self.assertIsNotNone(row.expires_at)
        delta = fields.Datetime.to_datetime(row.expires_at) - fields.Datetime.to_datetime(now)
        self.assertTrue(250 <= delta.total_seconds() <= 400)
