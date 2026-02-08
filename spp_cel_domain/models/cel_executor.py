from __future__ import annotations

import logging
from collections.abc import Iterable
from typing import Any

from odoo import api, models
from odoo.osv import expression
from odoo.tools.sql import SQL

from .cel_queryplan import (
    AND,
    NOT,
    OR,
    AggMetricCompare,
    CountThrough,
    CoverageRequire,
    ExistsThrough,
    LeafDomain,
    MetricCompare,
    flatten_and,
)


class CelExecutor(models.AbstractModel):
    _name = "cel.executor"
    _description = "CEL Executor"
    _logger = logging.getLogger("odoo.addons.spp_cel_domain")

    @api.model
    def compile_and_preview(self, model: str, expr: str, limit: int = 50) -> dict[str, Any]:
        import uuid

        cfg = self.env.context.get("cel_cfg") or {}
        translator = self.env["cel.translator"]
        plan, explain = translator.translate(model, expr, cfg)
        # Compose base domain
        base_domain = cfg.get("base_domain", [])
        metrics_info: list[dict[str, Any]] = []
        request_id = str(uuid.uuid4())
        domain, requires_exec = self._plan_to_domain(model, plan)
        final_domain = self._and_domains(base_domain, domain)
        count, ids = 0, []
        if requires_exec:
            # execute via search to compute parent ids when needed
            # propagate preview context for metrics evaluation
            exec_self = self.with_context(cel_mode="preview", cel_request_id=request_id)
            ids = exec_self._execute_plan(model, plan, metrics_info)
            # If a fast-path domain override was provided in metrics_info, use it instead of materializing ids
            override_domain: list[Any] | None = None
            for mi in metrics_info:
                od = mi.get("override_domain") if isinstance(mi, dict) else None
                if od:
                    override_domain = od
                    break
            if override_domain:
                final_domain = self._and_domains(base_domain, override_domain)
            else:
                final_domain = self._and_domains(base_domain, [("id", "in", ids)])
        # Log for visibility during tests
        try:
            self._logger.info(
                "[CEL EXEC] model=%s expr=%s explain=%s domain=%s exec=%s",
                model,
                expr,
                explain,
                final_domain,
                requires_exec,
            )
        except Exception:
            pass
        all_ids = self.env[model].search(final_domain).ids
        count = len(all_ids)
        rec_ids = all_ids[:limit] if limit else all_ids
        self.env[model].browse(rec_ids)
        # Enrich explanation with metrics info if any
        metrics_section = ""
        if metrics_info:
            parts = []
            for mi in metrics_info:
                # Add lightweight warnings
                warnings = []
                cov = float(mi.get("coverage") or 0.0)
                if cov < 0.8:
                    warnings.append("LOW_COVERAGE")
                if int(mi.get("misses") or 0) > 0:
                    warnings.append("CACHE_MISSES")
                if mi.get("provider_missing"):
                    warnings.append("PROVIDER_MISSING")
                if mi.get("cache_any_provider_used"):
                    warnings.append("CACHE_ANY_PROVIDER")
                mi["warnings"] = warnings
                parts.append(
                    f"metric={mi.get('metric')} period={mi.get('period_key')} "
                    f"requested={mi.get('requested')} cache_hits={mi.get('cache_hits')} "
                    f"fresh={mi.get('fresh_fetches')} coverage={round(cov*100,1)}%"
                    + (f" warnings={','.join(warnings)}" if warnings else "")
                )
            metrics_section = " | Metrics: " + "; ".join(parts)
            explain = f"{explain}{metrics_section}"
        return {
            "domain": final_domain,
            "domain_text": str(final_domain),
            "explain": explain,
            "explain_struct": {
                "metrics": metrics_info,
                "request_id": request_id,
            },
            "count": count,
            "ids": all_ids,
        }

    # Plan → Domain (best effort)
    def _plan_to_domain(self, model: str, plan: Any) -> tuple[list[Any], bool]:
        if isinstance(plan, LeafDomain):
            if plan.model != model:
                # different model; cannot express as dotted safely
                return [], True
            return plan.domain, False
        if isinstance(plan, AND):
            domains: list[Any] = []
            needs_exec = False
            for n in flatten_and(plan.nodes):
                d, e = self._plan_to_domain(model, n)
                needs_exec = needs_exec or e
                if d:
                    domains = self._and_domains(domains, d)
            return domains, needs_exec
        if isinstance(plan, OR):
            # if any side requires exec, mark as exec
            left, le = self._plan_to_domain(model, plan.nodes[0])
            right, re = self._plan_to_domain(model, plan.nodes[1])
            if le or re:
                return [], True
            return ["|", *left, *right], False
        if isinstance(plan, NOT):
            d, e = self._plan_to_domain(model, plan.node)
            if e:
                return [], True
            return ["!", *d], False
        if isinstance(plan, ExistsThrough | CountThrough):
            return [], True
        return [], True

    def _and_domains(self, a: list[Any], b: list[Any]) -> list[Any]:
        da = self._ensure_domain_list(a)
        db = self._ensure_domain_list(b)
        if not da:
            return db
        if not db:
            return da
        return expression.AND([da, db])

    def _ensure_domain_list(self, domain: list[Any]) -> list[Any]:
        if not domain:
            return []
        if isinstance(domain, list):
            normalized: list[Any] = []
            for term in list(domain):
                if (
                    isinstance(term, list)
                    and len(term) == 3
                    and term
                    and isinstance(term[0], str)
                    and term[0] not in {"&", "|", "!", "not"}
                ):
                    normalized.append(tuple(term))
                else:
                    normalized.append(term)
            return normalized
        return [domain]

    # Execute
    def _execute_plan(self, model: str, plan: Any, metrics_info: list[dict[str, Any]] | None = None) -> list[int]:  # noqa: C901
        if isinstance(plan, LeafDomain):
            return self.env[plan.model].search(plan.domain).ids
        if isinstance(plan, AND):
            # intersection
            id_sets = [set(self._execute_plan(model, p, metrics_info)) for p in flatten_and(plan.nodes)]
            if not id_sets:
                return []
            s = id_sets[0]
            for other in id_sets[1:]:
                s = s.intersection(other)
            return list(s)
        if isinstance(plan, OR):
            ids = set()
            for p in plan.nodes:
                ids.update(self._execute_plan(model, p, metrics_info))
            return list(ids)
        if isinstance(plan, NOT):
            # CRITICAL FIX: Do not load all IDs into memory (DoS risk on large datasets)
            domain, requires_exec = self._plan_to_domain(model, plan.node)
            if requires_exec:
                raise NotImplementedError(
                    "Negating complex expressions (like 'exists' or 'count') is not supported "
                    "due to performance constraints. Please restructure your expression to avoid "
                    "negating subqueries. For example, instead of 'not members.exists(m, P)', "
                    "try to express the positive condition."
                )
            # Use native Odoo domain negation instead of memory-based set operations
            negated_domain = ["!"] + domain
            return self.env[model].search(negated_domain).ids
        if isinstance(plan, ExistsThrough):
            return self._exec_exists(plan)
        if isinstance(plan, CountThrough):
            return self._exec_count(plan)
        if isinstance(plan, MetricCompare):
            return self._exec_metric(model, plan, metrics_info)
        if isinstance(plan, CoverageRequire):
            # Only support gating on MetricCompare results for now
            if not isinstance(plan.node, MetricCompare):
                raise NotImplementedError("require_coverage currently supports only metric() comparisons")
            # Evaluate metric comparison and get stats for coverage check
            tmp_stats: list[dict[str, Any]] = []
            ids = self._exec_metric(model, plan.node, tmp_stats)
            cov = 0.0
            if tmp_stats:
                cov = float(tmp_stats[-1].get("coverage") or 0.0)
                if metrics_info is not None:
                    metrics_info.extend(tmp_stats)
            if cov < float(plan.min_coverage or 0.0):
                return []
            return ids
        if isinstance(plan, AggMetricCompare):
            return self._exec_agg_metric(model, plan, metrics_info)
        return []

    def _exec_exists(self, p: ExistsThrough) -> list[int]:
        # Build membership domain, splitting child predicates to through-model vs child-model
        dom: list[Any] = []
        if p.default_domain:
            dom = self._and_domains(dom, p.default_domain)
        mem_dom, child_subplan = self._split_child_membership(p.through_model, p.child_plan)
        if mem_dom:
            dom = self._and_domains(dom, mem_dom)
        if child_subplan is not None:
            child_domain, requires_exec_child = self._plan_to_domain(p.child_model, child_subplan)
            try:
                self._logger.info(
                    "[CEL EXISTS] child_subplan model=%s plan=%s requires_exec=%s",
                    getattr(child_subplan, "model", None),
                    getattr(child_subplan, "domain", None),
                    requires_exec_child,
                )
            except Exception:
                pass
            if requires_exec_child:
                child_ids = self._execute_plan(p.child_model, child_subplan)
            else:
                child_domain = self._ensure_domain_list(child_domain)
                try:
                    self._logger.info("[CEL EXISTS] applying child domain=%s on model=%s", child_domain, p.child_model)
                except Exception:
                    pass
                child_ids = self.env[p.child_model].search(child_domain).ids
            child_ids = [int(i) for i in child_ids if i]
            if not child_ids:
                try:
                    self._logger.info(
                        "[CEL DEBUG EXISTS] child filter empty through=%s parent=%s child_model=%s "
                        "domain=%s requires_exec=%s",
                        p.through_model,
                        p.parent_field,
                        p.child_model,
                        child_domain,
                        requires_exec_child,
                    )
                except Exception:
                    pass
                return []
            dom = self._and_domains(dom, [(p.link_field, "in", child_ids)])
        rows = self.env[p.through_model].search(dom)
        # Debug: log domain size for troubleshooting
        try:
            self._logger.info(
                "[CEL EXEC EXISTS] through=%s parent=%s link=%s mem_dom=%s child_subplan=%s rows=%s",
                p.through_model,
                p.parent_field,
                p.link_field,
                dom,
                child_subplan.__class__.__name__ if child_subplan else None,
                len(rows),
            )
        except Exception:
            pass
        return list(set(rows.mapped(p.parent_field).ids))

    def _exec_count(self, p: CountThrough) -> list[int]:  # noqa: C901
        cfg = self.env.context.get("cel_cfg") or {}
        dom: list[Any] = []
        if p.default_domain:
            dom = self._and_domains(dom, p.default_domain)
        mem_dom, child_subplan = self._split_child_membership(p.through_model, p.child_plan)
        if mem_dom:
            dom = self._and_domains(dom, mem_dom)

        parent_model_name = None
        parent_field_desc = self.env[p.through_model]._fields.get(p.parent_field)
        if parent_field_desc is not None:
            parent_model_name = getattr(parent_field_desc, "comodel_name", None)

        base_domain: list[Any] = []
        if parent_model_name and cfg.get("root_model") == parent_model_name:
            if isinstance(cfg.get("base_domain"), list):
                base_domain = cfg.get("base_domain")

        candidate_parents: set[int] = set()
        if parent_model_name and base_domain:
            candidate_parents = set(int(pid) for pid in self.env[parent_model_name].search(base_domain).ids)

        if child_subplan is not None:
            child_domain, requires_exec_child = self._plan_to_domain(p.child_model, child_subplan)
            if requires_exec_child:
                child_ids = self._execute_plan(p.child_model, child_subplan)
            else:
                child_domain = self._ensure_domain_list(child_domain)
                try:
                    self._logger.info("[CEL EXISTS] applying child domain=%s on model=%s", child_domain, p.child_model)
                except Exception:
                    pass
                child_ids = self.env[p.child_model].search(child_domain).ids
            child_ids = [int(i) for i in child_ids if i]
            try:
                sample_labels = []
                if child_ids:
                    records = self.env[p.child_model].browse(child_ids[:5])
                    sample_labels = [
                        getattr(rec, "name", None) or getattr(rec, "display_name", None) for rec in records
                    ]
                self._logger.info(
                    "[CEL EXISTS] child filter results child_model=%s domain=%s ids=%s sample=%s",
                    p.child_model,
                    child_domain,
                    child_ids[:10],
                    sample_labels,
                )
            except Exception:
                pass
            if not child_ids:
                # No matching children; counts are zero for all candidate parents
                if not candidate_parents and parent_model_name:
                    search_domain = base_domain if base_domain else []
                    candidate_parents = set(int(pid) for pid in self.env[parent_model_name].search(search_domain).ids)
                return [pid for pid in candidate_parents if self._compare(0, p.op, p.rhs)]
            dom = self._and_domains(dom, [(p.link_field, "in", child_ids)])

        rows = self.env[p.through_model].read_group(dom, [p.parent_field], [p.parent_field])
        counts: dict[int, int] = {}
        for r in rows:
            count = int(r.get(f"{p.parent_field}_count") or 0)
            pid = r.get(p.parent_field)
            if isinstance(pid, tuple):
                pid = pid[0]
            if pid:
                counts[int(pid)] = count

        parent_ids: set[int] = set(counts.keys())
        if candidate_parents:
            parent_ids |= candidate_parents
        if not parent_ids and parent_model_name:
            search_domain = base_domain if base_domain else []
            parent_ids = set(int(pid) for pid in self.env[parent_model_name].search(search_domain).ids)

        res: list[int] = []
        for pid in parent_ids:
            if self._compare(counts.get(pid, 0), p.op, p.rhs):
                res.append(pid)
        return res

    def _compare(self, a: int, op: str, b: int) -> bool:
        return {
            "=": a == b,
            "==": a == b,
            ">": a > b,
            ">=": a >= b,
            "<": a < b,
            "<=": a <= b,
            "!=": a != b,
        }[op]

    def _split_child_membership(self, through_model: str, child_plan: Any) -> tuple[list[Any], Any]:
        """Split child_plan into membership-domain leaves (on through_model) and the residual
        child subplan to be evaluated on the child model. Only flattens simple AND plans.

        Returns (membership_domain, residual_plan_or_None).
        """
        # Direct leaf on through model
        if isinstance(child_plan, LeafDomain) and getattr(child_plan, "model", None) == through_model:
            return self._ensure_domain_list(child_plan.domain), None
        # For an AND, collect through-model leaves and keep the rest as residual
        if isinstance(child_plan, AND):
            mem_dom: list[Any] = []
            residual_nodes: list[Any] = []
            for n in flatten_and(child_plan.nodes):
                if isinstance(n, LeafDomain) and getattr(n, "model", None) == through_model:
                    sub_domain = self._ensure_domain_list(n.domain)
                    if sub_domain:
                        mem_dom = self._and_domains(mem_dom, sub_domain)
                else:
                    residual_nodes.append(n)
            if not residual_nodes:
                return mem_dom, None
            if len(residual_nodes) == 1:
                return mem_dom, residual_nodes[0]
            return mem_dom, AND(residual_nodes)
        # Fallback: cannot split
        return [], child_plan

    def _exec_metric(self, model: str, p: MetricCompare, metrics_info: list[dict[str, Any]] | None = None) -> list[int]:
        """Evaluate metric comparison and return matching subject IDs for current model.

        Uses openspp.metrics service with mode=fallback.
        """
        cfg = self.env.context.get("cel_cfg") or {}
        base_dom = cfg.get("base_domain", []) if isinstance(cfg.get("base_domain"), list) else []
        period_key = str(p.period_key or "default")
        subject_model = model
        # Resolve flags
        ICP = self.env["ir.config_parameter"].sudo()
        enable_sql = bool(int(ICP.get_param("cel.enable_sql_metrics", "1")))
        preview_cache_only = bool(int(ICP.get_param("cel.preview_cache_only", "0")))
        async_threshold = int(ICP.get_param("cel.async_threshold", "50000") or 50000)
        allow_any_provider = self._allow_any_provider_fallback()
        # Provider resolution
        provider, return_type = self._metric_registry_info(p.metric)
        params_hash = ""  # CEL V2: no params by default
        # Preflight completeness/freshness
        status = self._metric_cache_status_sql(
            subject_model,
            base_dom,
            p.metric,
            period_key,
            provider,
            params_hash,
            allow_any_provider,
        )
        path = "python"
        # SQL fast path
        rhs = p.rhs
        if enable_sql and status.get("status") == "fresh" and self._metric_cmp_supported(p.op, rhs, return_type):
            sql = self._metric_inselect_sql(
                subject_model,
                p.metric,
                period_key,
                provider,
                params_hash,
                p.op,
                rhs,
                return_type,
                allow_any_provider,
            )
            domain = [("id", "in", sql)]
            path = "sql"
            if metrics_info is not None:
                mi = dict(status)
                mi.update({"metric": p.metric, "period_key": period_key, "path": path, "override_domain": domain})
                metrics_info.append(mi)
            # We return [] and let compile_and_preview use override_domain to avoid
            # materializing ids into a huge 'in' list
            return []
        # Preview mode behavior when not fresh
        cel_mode = self.env.context.get("cel_mode")
        preview_cache_only_mode = cel_mode == "preview" and preview_cache_only
        # Evaluate/batch or preview fallback (small cohorts): compute via service
        # Compute candidate size cheaply via search_count
        base_count = self.env[subject_model].search_count(base_dom)
        svc = self.env["openspp.indicator"]
        default_mode = "refresh" if (base_count < async_threshold) else "fallback"
        if default_mode == "fallback" and status.get("status") != "fresh" and not preview_cache_only_mode:
            # large + not fresh → enqueue refresh and report queued
            svc.enqueue_refresh_from_domain(p.metric, subject_model, list(base_dom), period_key)
            if metrics_info is not None:
                mi = dict(status)
                mi.update({"metric": p.metric, "period_key": period_key, "path": "queued"})
                metrics_info.append(mi)
            return []
        # Small cohort (or already fresh) → refresh synchronously then filter in Python
        aggregated_values: dict[int, Any] = {}
        stats_total: dict[str, Any] = {
            "requested": 0,
            "cache_hits": 0,
            "misses": 0,
            "fresh_fetches": 0,
            "coverage": 0.0,
            "metric": p.metric,
            "period_key": period_key,
            "provider": provider,
            "params_hash": params_hash,
            "company_id": self.env.company.id,
            "provider_missing": False,
            "cache_any_provider_used": False,
        }
        if preview_cache_only_mode:
            eval_mode = "cache_only"
        else:
            eval_mode = "refresh" if status.get("status") != "fresh" else "fallback"
        total_requested = 0
        for batch_ids in self._iter_domain_ids(subject_model, base_dom):
            if not batch_ids:
                continue
            total_requested += len(batch_ids)
            batch_values, batch_stats = svc.evaluate(p.metric, subject_model, batch_ids, period_key, mode=eval_mode)
            aggregated_values.update(batch_values)
            if batch_stats:
                stats_total["cache_hits"] += int(batch_stats.get("cache_hits") or 0)
                stats_total["misses"] += int(batch_stats.get("misses") or 0)
                stats_total["fresh_fetches"] += int(batch_stats.get("fresh_fetches") or 0)
                stats_total["cache_any_provider_used"] = stats_total["cache_any_provider_used"] or bool(
                    batch_stats.get("cache_any_provider_used")
                )
                stats_total["provider_missing"] = stats_total["provider_missing"] or bool(
                    batch_stats.get("provider_missing")
                )
                stats_total["provider"] = batch_stats.get("provider") or stats_total["provider"]
        if total_requested:
            stats_total["requested"] = total_requested
            stats_total["coverage"] = len(aggregated_values) / float(base_count or 1)
        incomplete_cache = eval_mode == "cache_only" and total_requested and len(aggregated_values) < total_requested
        if eval_mode == "cache_only":
            path_flag = "cache_only"
        else:
            path_flag = "python" if status.get("status") != "fresh" else "cache"
        stats_total.update({"path": path_flag})
        if incomplete_cache:
            if metrics_info is not None:
                metrics_info.append(stats_total)
            return []
        if metrics_info is not None:
            metrics_info.append(stats_total)
        res = []
        for sid, val in aggregated_values.items():
            v = val
            if self._cmp_value(v, p.op, p.rhs):
                res.append(int(sid))
        return res

    def _metric_registry_info(self, metric: str) -> tuple[str, str]:
        info = self.env["openspp.indicator.registry"].get(metric) or {}
        provider = info.get("provider") or metric
        return_type = info.get("return_type") or "json"
        return provider, return_type

    def _metric_cmp_supported(self, op: str, rhs: Any, return_type: str) -> bool:
        if isinstance(rhs, int | float):
            return op in {"==", "!=", ">", ">=", "<", "<="}
        if isinstance(rhs, str):
            return op in {"==", "!="}
        # non-scalar comparisons not supported in SQL fast path yet
        return False

    def _metric_cache_status_sql(
        self,
        model: str,
        base_domain: list[Any],
        metric: str,
        period_key: str,
        provider: str,
        params_hash: str,
        allow_any_provider: bool,
    ) -> dict[str, Any]:
        # base count with record rules
        base_count = self.env[model].search_count(base_domain)
        # subquery for “have any row” irrespective of expiry
        have_dom = self._and_domains(
            list(base_domain),
            [
                (
                    "id",
                    "in",
                    self._feature_value_subquery(
                        metric,
                        model,
                        period_key,
                        provider,
                        params_hash,
                        "",
                        allow_any_provider,
                    ),
                )
            ],
        )
        have_count = self.env[model].search_count(have_dom)
        # subquery for stale rows
        stale_dom = self._and_domains(
            list(base_domain),
            [
                (
                    "id",
                    "in",
                    self._feature_value_subquery(
                        metric,
                        model,
                        period_key,
                        provider,
                        params_hash,
                        "AND fv.expires_at IS NOT NULL AND fv.expires_at <= NOW()",
                        allow_any_provider,
                    ),
                )
            ],
        )
        stale_count = self.env[model].search_count(stale_dom)
        status = "fresh"
        if have_count < base_count:
            status = "incomplete"
        if stale_count > 0:
            status = "stale"
        self._logger.info(
            "[CEL Metrics] cache status model=%s metric=%s period=%s provider=%s base=%s have=%s stale=%s status=%s",
            model,
            metric,
            period_key,
            provider,
            base_count,
            have_count,
            stale_count,
            status,
        )
        return {"status": status, "base": base_count, "have": have_count, "stale": stale_count}

    def _metric_inselect_sql(
        self,
        model: str,
        metric: str,
        period_key: str,
        provider: str,
        params_hash: str,
        op: str,
        rhs: Any,
        return_type: str,
        allow_any_provider: bool,
    ) -> SQL:
        num_ops = {"==": "=", "!=": "!=", ">": ">", ">=": ">=", "<": "<", "<=": "<="}
        str_ops = {"==": "=", "!=": "!="}
        clause, clause_args = self._provider_clause(provider, params_hash, allow_any_provider)
        base_sql = (
            "SELECT DISTINCT fv.subject_id FROM openspp_indicator_value fv "
            "WHERE fv.company_id = %s AND fv.metric = %s AND fv.subject_model = %s "
            "AND fv.period_key = %s AND ("
            + clause
            + ") AND fv.error_code IS NULL AND (fv.expires_at IS NULL OR fv.expires_at > NOW()) "
        )
        base_args: tuple[Any, ...] = (
            self.env.company.id,
            metric,
            model,
            period_key,
            *clause_args,
        )
        if isinstance(rhs, int | float):
            return SQL(
                "(%s)",
                SQL(
                    base_sql
                    + "AND jsonb_typeof(fv.value_json) = 'number' AND (fv.value_json::numeric) "
                    + num_ops[op]
                    + " %s",
                    *base_args,
                    rhs,
                ),
            )
        if isinstance(rhs, str):
            return SQL(
                "(%s)",
                SQL(
                    base_sql + "AND jsonb_typeof(fv.value_json) = 'string' "
                    "AND (fv.value_json #>> '{}') " + str_ops[op] + " %s",
                    *base_args,
                    rhs,
                ),
            )
        # Fallback should not be called for unsupported types
        return SQL(
            "(%s)",
            SQL(base_sql + "AND 1=0", *base_args),
        )

    def _feature_value_subquery(
        self,
        metric: str,
        model: str,
        period_key: str,
        provider: str,
        params_hash: str,
        extra_clause: str,
        allow_any_provider: bool,
    ) -> SQL:
        clause, clause_args = self._provider_clause(provider, params_hash, allow_any_provider)
        tail = f" {extra_clause}" if extra_clause else ""
        sql = (
            "SELECT DISTINCT fv.subject_id FROM openspp_indicator_value fv "
            "WHERE fv.company_id = %s AND fv.metric = %s AND fv.subject_model = %s "
            "AND fv.period_key = %s AND (" + clause + ") AND fv.error_code IS NULL" + tail
        )
        args: tuple[Any, ...] = (
            self.env.company.id,
            metric,
            model,
            period_key,
            *clause_args,
        )
        return SQL("(%s)", SQL(sql, *args))

    def _provider_clause(self, provider: str, params_hash: str, allow_any_provider: bool) -> tuple[str, list[Any]]:
        provider = provider or ""
        params_hash = params_hash or ""
        combos: list[tuple[str, str]] = [
            (provider, params_hash),
        ]
        if provider:
            combos.append(("", params_hash))
        if params_hash:
            combos.append((provider, ""))
        combos.append(("", ""))
        # Deduplicate while preserving order
        seen = set()
        uniq_combos: list[tuple[str, str]] = []
        for combo in combos:
            if combo not in seen:
                seen.add(combo)
                uniq_combos.append(combo)
        clauses: list[str] = []
        args: list[Any] = []
        for prov, phash in uniq_combos:
            clauses.append("(fv.provider = %s AND fv.params_hash = %s)")
            args.extend([prov, phash])
        if allow_any_provider:
            clauses.append("(fv.params_hash = %s)")
            args.append(params_hash)
        return " OR ".join(clauses), args

    def _allow_any_provider_fallback(self) -> bool:
        try:
            value = self.env["ir.config_parameter"].sudo().get_param("openspp_metrics.allow_any_provider_fallback", "1")
            return bool(int(value or "1"))
        except Exception:
            return True

    def _iter_domain_ids(self, model: str, domain: list[Any], batch_size: int = 2000) -> Iterable[list[int]]:
        Model = self.env[model]
        base_domain = self._ensure_domain_list(domain)
        last_id = 0
        while True:
            if last_id:
                batch_domain = self._and_domains(base_domain, [("id", ">", last_id)])
            else:
                batch_domain = list(base_domain)
            records = Model.search(batch_domain, limit=batch_size, order="id")
            if not records:
                break
            ids = [int(i) for i in records.ids]
            yield ids
            last_id = ids[-1]
            if len(ids) < batch_size:
                break

    def _cmp_value(self, a: Any, op: str, b: Any) -> bool:
        # Attempt numeric comparison when possible
        def to_num(x):
            try:
                return float(x)
            except Exception:
                return x

        ax = to_num(a)
        bx = to_num(b)
        ops = {
            "==": lambda x, y: x == y,
            "!=": lambda x, y: x != y,
            ">": lambda x, y: x > y,
            ">=": lambda x, y: x >= y,
            "<": lambda x, y: x < y,
            "<=": lambda x, y: x <= y,
        }
        try:
            return ops[op](ax, bx)
        except Exception:
            return False

    def _exec_agg_metric(  # noqa: C901
        self, model: str, p: AggMetricCompare, metrics_info: list[dict[str, Any]] | None
    ) -> list[int]:
        """Evaluate an aggregate of a metric over a through relation.

        Strategy:
        - Collect membership rows (default_domain applied)
        - Build parent -> [child_ids] mapping
        - Evaluate metric for union(child_ids)
        - Compute aggregator per parent and compare vs rhs
        """
        dom: list[Any] = []
        if p.default_domain:
            dom.extend(p.default_domain)
        rows = self.env[p.through_model].search(dom)
        if not rows:
            return []
        parent_map: dict[int, list[int]] = {}
        for r in rows:
            try:
                pid = int(
                    getattr(r, p.parent_field).id
                    if hasattr(getattr(r, p.parent_field), "id")
                    else getattr(r, p.parent_field)
                )
                cid = int(
                    getattr(r, p.link_field).id if hasattr(getattr(r, p.link_field), "id") else getattr(r, p.link_field)
                )
            except Exception:
                continue
            parent_map.setdefault(pid, []).append(cid)
        # Evaluate the metric for all distinct child ids
        all_child_ids = sorted({cid for lst in parent_map.values() for cid in lst})
        if not all_child_ids:
            return []
        svc = self.env["openspp.indicator"]
        values, stats = svc.evaluate(
            p.metric, p.child_model, all_child_ids, str(p.period_key or "default"), mode="fallback"
        )
        if metrics_info is not None and stats:
            metrics_info.append(dict(stats, metric=p.metric, period_key=str(p.period_key or "default")))
        winners: list[int] = []
        for pid, cids in parent_map.items():
            vals = []
            present = 0
            for cid in cids:
                v = values.get(cid)
                if v is not None:
                    present += 1
                    vals.append(v)
            if p.agg == "avg":
                nums: list[float] = []
                for v in vals:
                    try:
                        nums.append(float(v))
                    except Exception:
                        continue
                if not nums:
                    continue
                agg_val = sum(nums) / len(nums)
            elif p.agg == "coverage":
                denom = len(cids) or 1
                agg_val = float(present) / float(denom)
            else:  # all
                # Treat missing as False (fail-closed)
                ok = True
                for cid in cids:
                    v = values.get(cid)
                    if v is None:
                        ok = False
                        break
                    if not self._cmp_value(v, p.op, p.rhs):
                        ok = False
                        break
                if ok:
                    winners.append(pid)
                continue
            if self._cmp_value(agg_val, p.op, p.rhs):
                winners.append(pid)
        return winners
