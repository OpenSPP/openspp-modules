from datetime import timedelta
from importlib import import_module
from unittest.mock import patch

from odoo import fields
from odoo.tests import common, tagged


@tagged("post_install", "-at_install", "cel_domain", "fastpath")
class TestMetricsSqlFastPath(common.TransactionCase):
    def setUp(self):
        super().setUp()
        ICP = self.env["ir.config_parameter"].sudo()
        ICP.set_param("cel.enable_sql_metrics", "1")
        ICP.set_param("cel.preview_cache_only", "1")
        # small threshold so evaluate path is not triggered in preview
        ICP.set_param("cel.async_threshold", "50000")

        Partner = self.env["res.partner"]
        # Use a unique email pattern to build a selective base_domain for preview
        self.p_ok = Partner.create({"name": "SQL FP A", "email": "fastpath@test.local", "is_registrant": True})
        self.p_ko = Partner.create({"name": "SQL FP B", "email": "fastpath@test.local", "is_registrant": True})

        self.metric = "perf.att"
        self.period = "2024-09"
        self.seed_values = {}

        class _FakeProvider:
            def __init__(self, test_case):
                self._test = test_case

            def compute_batch(self, env, ctx, subject_ids):
                return {sid: self._test.seed_values.get(sid) for sid in subject_ids if sid in self._test.seed_values}

        self.env["openspp.indicator.registry"].register(
            self.metric,
            _FakeProvider(self),
            return_type="number",
            provider=self.metric,
            capabilities={"default_ttl": 3600},
        )

    def _seed_cache(self, rows):
        now_str = fields.Datetime.now()
        now_dt = fields.Datetime.to_datetime(now_str)
        later = now_dt + timedelta(hours=1)
        rows_payload = [
            {
                "metric": self.metric,
                "provider": self.metric,
                "subject_model": "res.partner",
                "subject_id": sid,
                "period_key": self.period,
                "value_json": val,
                "value_type": "number"
                if isinstance(val, int | float)
                else ("string" if isinstance(val, str) else "json"),
                "as_of": now_str,
                "fetched_at": now_str,
                "expires_at": later,
                "source": "test",
                "company_id": self.env.company.id,
            }
            for sid, val in rows
        ]
        self.env["openspp.indicator.value"].sudo().upsert_values(rows_payload)
        self.seed_values = {sid: val for sid, val in rows}

    def test_sql_fast_path_numeric(self):
        # Seed both rows, only one meets >= 85
        self._seed_cache(
            [
                (self.p_ok.id, 92),
                (self.p_ko.id, 70),
            ]
        )
        cfg = {"root_model": "res.partner", "base_domain": [("email", "ilike", "fastpath@test.local")]}
        expr = f'metric("{self.metric}", me, "{self.period}") >= 85'
        res = self.env["cel.executor"].with_context(cel_cfg=cfg).compile_and_preview("res.partner", expr, limit=100)
        # Should return only p_ok
        assert res["ids"] == [self.p_ok.id]
        # Metrics explain should indicate SQL path and provide an override_domain
        metrics = res["explain_struct"].get("metrics") or []
        assert metrics, "expected metrics info in explain_struct"
        assert any(m.get("path") == "sql" for m in metrics)
        assert any(isinstance(m.get("override_domain"), list) for m in metrics)

    def test_preview_cache_only_incomplete(self):
        # Seed only one partner -> incomplete cache
        self._seed_cache([(self.p_ok.id, 90)])
        cfg = {"root_model": "res.partner", "base_domain": [("email", "ilike", "fastpath@test.local")]}
        expr = f'metric("{self.metric}", me, "{self.period}") >= 85'
        res = self.env["cel.executor"].with_context(cel_cfg=cfg).compile_and_preview("res.partner", expr, limit=100)
        # In preview cache-only mode, we should not compute; return no ids
        assert res["ids"] == []
        metrics = res["explain_struct"].get("metrics") or []
        assert any(m.get("path") == "cache_only" for m in metrics)
        assert any((m.get("coverage") or 0) < 1 for m in metrics)

    def test_evaluate_large_cohort_enqueues_refresh(self):
        # Incomplete cache over 2 partners triggers enqueue in evaluate mode when threshold=1
        ICP = self.env["ir.config_parameter"].sudo()
        ICP.set_param("cel.async_threshold", "1")
        # Seed only p_ok
        self._seed_cache([(self.p_ok.id, 90)])
        cfg = {"root_model": "res.partner", "base_domain": [("email", "ilike", "fastpath@test.local")]}
        expr = f'metric("{self.metric}", me, "{self.period}") >= 85'
        Translator = self.env["cel.translator"]
        plan, _ = Translator.translate("res.partner", expr, cfg)
        calls = {}
        # Patch enqueue_refresh to capture calls without relying on queue_job runtime
        OpensppIndicatorService = import_module("odoo.addons.spp_indicators.models.service").OpensppIndicatorService

        def _fake_enqueue(self_, metric, subject_model, subject_ids, period_key, *, chunk_size=2000):
            calls["metric"] = metric
            calls["subject_model"] = subject_model
            calls["period_key"] = period_key
            calls["count"] = len(subject_ids)
            return 1

        with patch.object(OpensppIndicatorService, "enqueue_refresh", _fake_enqueue):
            metrics_info = []
            _ = (
                self.env["cel.executor"]
                .with_context(cel_mode="evaluate", cel_cfg=cfg)
                ._execute_plan("res.partner", plan, metrics_info)
            )
        # Ensure enqueue was called and path is 'queued'
        assert calls.get("metric") == self.metric
        assert any(mi.get("path") == "queued" for mi in metrics_info), metrics_info

    def test_sql_fast_path_string(self):
        self._seed_cache(
            [
                (self.p_ok.id, "active"),
                (self.p_ko.id, "inactive"),
            ]
        )
        cfg = {"root_model": "res.partner", "base_domain": [("email", "ilike", "fastpath@test.local")]}
        expr = f'metric("{self.metric}", me, "{self.period}") == "active"'
        res = self.env["cel.executor"].with_context(cel_cfg=cfg).compile_and_preview("res.partner", expr, limit=100)
        assert res["ids"] == [self.p_ok.id]
        metrics = res["explain_struct"].get("metrics") or []
        assert any(m.get("path") == "sql" for m in metrics)

    def test_sql_fast_path_respects_record_rules(self):
        self._seed_cache(
            [
                (self.p_ok.id, 95),
                (self.p_ko.id, 60),
            ]
        )
        group = self.env["res.groups"].create({"name": "CEL Fastpath Limited"})
        self.env["ir.rule"].create(
            {
                "name": "Limit Fastpath Partner",
                "model_id": self.env.ref("base.model_res_partner").id,
                "domain_force": "[('id', '=', %d)]" % self.p_ok.id,
                "groups": [(4, group.id)],
            }
        )
        user = (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Fastpath Restricted",
                    "login": "fastpath.user@example.com",
                    "email": "fastpath.user@example.com",
                    "groups_id": [(6, 0, [group.id, self.env.ref("base.group_user").id])],
                }
            )
        )
        cfg = {"root_model": "res.partner", "base_domain": [("email", "ilike", "fastpath@test.local")]}
        expr = f'metric("{self.metric}", me, "{self.period}") >= 80'
        res = (
            self.env["cel.executor"]
            .with_context(cel_cfg=cfg)
            .with_user(user)
            .compile_and_preview("res.partner", expr, limit=100)
        )
        assert res["ids"] == [self.p_ok.id]

    def test_preflight_status_transitions(self):
        executor = self.env["cel.executor"]
        base_domain = [("email", "ilike", "fastpath@test.local")]
        provider = self.metric
        params_hash = ""
        # fresh: both rows present, not expired
        self._seed_cache([(self.p_ok.id, 90), (self.p_ko.id, 88)])
        allow_any_provider = executor._allow_any_provider_fallback()
        status_fresh = executor._metric_cache_status_sql(
            "res.partner", base_domain, self.metric, self.period, provider, params_hash, allow_any_provider
        )
        assert status_fresh["status"] == "fresh"

        # incomplete: remove one row
        self.env["openspp.indicator.value"].sudo().search(
            [
                ("metric", "=", self.metric),
                ("subject_id", "=", self.p_ko.id),
                ("period_key", "=", self.period),
            ]
        ).unlink()
        status_incomplete = executor._metric_cache_status_sql(
            "res.partner", base_domain, self.metric, self.period, provider, params_hash, allow_any_provider
        )
        assert status_incomplete["status"] == "incomplete"

        # stale: restore row and mark expired
        self._seed_cache([(self.p_ko.id, 88)])
        self.env.cr.execute(
            """
            UPDATE openspp_indicator_value SET expires_at = NOW() - interval '1 minute'
            WHERE metric = %s AND subject_id = %s AND period_key = %s
            """,
            (self.metric, self.p_ok.id, self.period),
        )
        status_stale = executor._metric_cache_status_sql(
            "res.partner", base_domain, self.metric, self.period, provider, params_hash, allow_any_provider
        )
        assert status_stale["status"] == "stale"

    def test_small_cohort_sync_refresh(self):
        ICP = self.env["ir.config_parameter"].sudo()
        ICP.set_param("cel.enable_sql_metrics", "0")
        ICP.set_param("cel.async_threshold", "1000")
        self._seed_cache([(self.p_ok.id, 82), (self.p_ko.id, 84)])
        cfg = {"root_model": "res.partner", "base_domain": [("email", "ilike", "fastpath@test.local")]}
        expr = f'metric("{self.metric}", me, "{self.period}") >= 80'
        FV = self.env["openspp.indicator.value"].sudo()
        assert (
            FV.search_count(
                [
                    ("metric", "=", self.metric),
                    ("subject_model", "=", "res.partner"),
                    ("provider", "=", self.metric),
                    ("period_key", "=", self.period),
                    ("subject_id", "in", [self.p_ok.id, self.p_ko.id]),
                ]
            )
            == 2
        )
        translator = self.env["cel.translator"]
        plan, _ = translator.translate("res.partner", expr, cfg)
        metrics_info = []
        ids = (
            self.env["cel.executor"]
            .with_context(cel_mode="evaluate", cel_cfg=cfg)
            ._execute_plan("res.partner", plan, metrics_info)
        )
        assert set(ids) == {self.p_ok.id, self.p_ko.id}
        assert any(mi.get("path") in {"cache", "python"} for mi in metrics_info)
