from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from odoo import api, fields, models

_logger = logging.getLogger(__name__)
_PARAMS_UNSPECIFIED = object()


class OpensppIndicatorService(models.AbstractModel):
    _name = "openspp.indicator"
    _description = "OpenSPP Indicator Service"

    @api.model
    def evaluate(  # noqa: C901
        self,
        metric: str,
        subject_model: str,
        subject_ids: list[int],
        period_key: str,
        *,
        mode: str = "fallback",
        params: Any = _PARAMS_UNSPECIFIED,
    ) -> tuple[dict[int, Any], dict[str, Any]]:
        """Evaluate a metric for many subjects.

        - mode: 'cache_only' | 'refresh' | 'fallback'
        Returns mapping subject_id -> value (native python; numbers/strings or JSON)
        """
        params = params or {}
        subject_ids = list({int(s) for s in subject_ids if s})
        if not subject_ids:
            return {}, {
                "requested": 0,
                "cache_hits": 0,
                "misses": 0,
                "fresh_fetches": 0,
                "coverage": 0.0,
                "metric": metric,
                "period_key": period_key,
            }

        feature = self.env["openspp.indicator.value"]
        registry = self.env["openspp.indicator.registry"]
        provider_info = registry.get(metric)
        company_id = self.env.company.id
        definition = (
            self.env["openspp.indicator.definition"]
            .sudo()
            .search(
                [
                    ("name", "=", metric),
                    ("company_id", "=", company_id),
                    ("active", "=", True),
                ],
                limit=1,
            )
        )
        provider_name = (provider_info or {}).get("provider") or metric
        # Build params hash for cache key (stable JSON)
        import hashlib as _hashlib
        import json as _json

        params_specified = params is not _PARAMS_UNSPECIFIED and params is not None
        params_norm: dict[str, Any] = {}
        if params_specified:
            if isinstance(params, dict):
                params_norm = params
            else:
                params_norm = dict(params or {})
        params_hash = ""
        if params_specified:
            try:
                params_json = _json.dumps(params_norm, sort_keys=True, separators=(",", ":"))
            except Exception:
                params_json = ""
            else:
                params_hash = _hashlib.sha1(params_json.encode("utf-8")).hexdigest() if params_json else ""
        else:
            params_norm = {}
        # Apply provider config (optional, non-invasive overrides); avoid querying if table missing
        cfg_rec = None
        try:
            self.env.cr.execute("SELECT to_regclass('public.openspp_indicator_provider')")
            exists = self.env.cr.fetchone()[0]
            if exists:
                # company = self.env["res.company"].browse(company_id)
                Provider = self.env["openspp.indicator.provider"].with_company(self.env.company).sudo()
                domain_common = [("metric", "=", metric), ("company_id", "=", company_id)]
                if provider_name:
                    cfg_rec = Provider.search(domain_common + [("name", "=", provider_name)], limit=1)
                if not cfg_rec:
                    cfg_rec = Provider.search(domain_common, order="write_date desc, id desc", limit=1)
        except Exception:
            cfg_rec = None
        now = fields.Datetime.now()
        # 1) Try cache/feature store
        cached = feature.read_values(
            metric,
            subject_model,
            subject_ids,
            period_key,
            provider=provider_name,
            params_hash=params_hash,
            company_id=company_id,
        )
        # Backward compatibility: if nothing found under provider key, try provider="" and finally params_hash=""
        if not cached:
            cached = feature.read_values(
                metric,
                subject_model,
                subject_ids,
                period_key,
                provider="",
                params_hash=params_hash,
                company_id=company_id,
            )
        # Also try the HTTP push default provider label "push" (explicit fallback)
        if not cached:
            cached = feature.read_values(
                metric,
                subject_model,
                subject_ids,
                period_key,
                provider="push",
                params_hash=params_hash,
                company_id=company_id,
            )
        if not cached and not params_specified:
            cached = feature.read_values(
                metric,
                subject_model,
                subject_ids,
                period_key,
                provider=provider_name,
                params_hash=None,
                company_id=company_id,
            )
        if not cached and not params_specified:
            cached = feature.read_values(
                metric,
                subject_model,
                subject_ids,
                period_key,
                provider="",
                params_hash=None,
                company_id=company_id,
            )
        if not cached and not params_specified:
            cached = feature.read_values(
                metric,
                subject_model,
                subject_ids,
                period_key,
                provider="push",
                params_hash=None,
                company_id=company_id,
            )
        if not cached and params_hash and not params_norm:
            cached = feature.read_values(
                metric, subject_model, subject_ids, period_key, provider="", params_hash="", company_id=company_id
            )
        if not cached and params_hash and not params_norm:
            cached = feature.read_values(
                metric,
                subject_model,
                subject_ids,
                period_key,
                provider="push",
                params_hash="",
                company_id=company_id,
            )
        # Last resort: ignore provider (e.g., registry not loaded but cache exists)
        cache_any_provider_used = False
        if not cached:
            # Controlled by setting; default True for dev-friendly behavior
            allow_any_provider = True
            try:
                allow_any_provider = bool(
                    int(
                        self.env["ir.config_parameter"]
                        .sudo()
                        .get_param("openspp_metrics.allow_any_provider_fallback", "1")
                    )
                )
            except Exception:
                allow_any_provider = True
            if allow_any_provider:
                try:
                    cached = feature.read_values_any_provider(
                        metric,
                        subject_model,
                        subject_ids,
                        period_key,
                        params_hash=(params_hash if params_specified else None),
                        company_id=company_id,
                    )
                    if cached:
                        cache_any_provider_used = True
                except Exception:
                    cached = {}
        values: dict[int, Any] = {}
        missing: list[int] = []
        for sid in subject_ids:
            row = cached.get(sid)
            if row and row.get("value") is not None:
                exp = row.get("expires_at")
                if mode == "refresh":
                    values[sid] = row["value"]
                    missing.append(sid)
                elif mode == "fallback" and exp and exp < now:
                    missing.append(sid)
                else:
                    values[sid] = row["value"]
            else:
                missing.append(sid)

        # 2) If refresh/fallback, and provider exists, compute for missing (micro-batched)
        fresh_fetches = 0
        if missing and provider_info and mode in ("refresh", "fallback"):
            handler = provider_info.get("handler")
            caps = dict(provider_info.get("capabilities") or {})
            # Override from provider config if present
            if cfg_rec:
                if cfg_rec.max_batch_size:
                    caps["max_batch_size"] = cfg_rec.max_batch_size
                if cfg_rec.default_ttl:
                    caps["default_ttl"] = cfg_rec.default_ttl
            if definition and not caps.get("default_ttl") and definition.default_ttl_seconds:
                caps["default_ttl"] = definition.default_ttl_seconds
            max_batch = int(caps.get("max_batch_size") or 5000)
            # TTL
            default_ttl = int(caps.get("default_ttl") or 0)
            if not default_ttl:
                try:
                    default_ttl = int(
                        self.env["ir.config_parameter"].sudo().get_param("openspp_metrics.default_ttl") or 0
                    )
                except Exception:
                    default_ttl = 0
            expires_at = fields.Datetime.to_datetime(now) + timedelta(seconds=default_ttl) if default_ttl else None
            # Process in chunks
            for i in range(0, len(missing), max_batch):
                batch_ids = missing[i : i + max_batch]
                # Optional ID mapping chain per batch
                mapped = {}
                unmapped: list[int] = []
                idmap = dict(provider_info.get("id_mapping") or {})
                if definition and definition.get_mapping_fields() and not idmap.get("fields"):
                    idmap["fields"] = definition.get_mapping_fields()
                if definition and definition.id_mapping_required and "required" not in idmap:
                    idmap["required"] = True
                if cfg_rec and cfg_rec.id_mapping_fields:
                    idmap["fields"] = [s.strip() for s in (cfg_rec.id_mapping_fields or "").split(",") if s.strip()]
                    idmap["required"] = bool(cfg_rec.id_mapping_required)
                if idmap:
                    fields_chain = idmap.get("fields") or []
                    required = bool(idmap.get("required"))
                    mapped, unmapped = self._map_subject_ids(subject_model, batch_ids, fields_chain, required=required)
                # Build evaluation context for provider
                ctx = {
                    "metric": metric,
                    "subject_model": subject_model,
                    "period_key": period_key,
                    "params": params_norm,
                    "mapped_subjects": mapped,
                    "unmapped_subjects": unmapped,
                    "mode": (self.env.context.get("cel_mode") or "preview" if mode == "fallback" else "evaluate"),
                    "request_id": (self.env.context.get("cel_request_id") or self.env.context.get("request_id")),
                    "deadline_ms": int(
                        self.env.context.get("cel_deadline_ms") or (2000 if mode == "fallback" else 10000)
                    ),
                    "company_id": company_id,
                }
                try:
                    computed = handler.compute_batch(self.env, ctx, batch_ids)
                except Exception as e:
                    _logger.exception("[openspp.indicator] provider %s failed: %s", metric, e)
                    computed = {}
                rows = []
                for sid, val in (computed or {}).items():
                    cov = None
                    out_val = val
                    if isinstance(val, dict) and "value" in val:
                        out_val = val.get("value")
                        cov = val.get("coverage")
                    rows.append(
                        {
                            "metric": metric,
                            "provider": provider_name,
                            "subject_model": subject_model,
                            "subject_id": int(sid),
                            "period_key": period_key,
                            "value_json": out_val,
                            "value_type": self._infer_type(out_val),
                            "params_hash": params_hash,
                            "coverage": cov,
                            "as_of": ctx.get("as_of") or now,
                            "fetched_at": now,
                            "expires_at": expires_at,
                            "source": "provider",
                            "company_id": company_id,
                        }
                    )
                if rows:
                    feature.sudo().upsert_values(rows)
                    for sid, val in (computed or {}).items():
                        out_val = val.get("value") if isinstance(val, dict) and "value" in val else val
                        values[int(sid)] = out_val
                    fresh_fetches += len(rows)
        requested = len(subject_ids)
        cache_hits = requested - len(missing)
        misses = len(missing)
        coverage = (len(values) / requested) if requested else 0.0
        stats = {
            "requested": requested,
            "cache_hits": cache_hits,
            "misses": misses,
            "fresh_fetches": fresh_fetches,
            "coverage": coverage,
            "metric": metric,
            "period_key": period_key,
            "provider": provider_name,
            "params_hash": params_hash,
            "company_id": company_id,
            "provider_missing": provider_info is None,
            "cache_any_provider_used": cache_any_provider_used,
        }
        return values, stats

    def _infer_type(self, v: Any) -> str:
        if isinstance(v, int | float):
            return "number"
        if isinstance(v, str):
            return "string"
        return "json"

    def _map_subject_ids(
        self, subject_model: str, subject_ids: list[int], fields_chain: list[str], *, required: bool = False
    ) -> tuple[dict[int, Any], list[int]]:
        if not fields_chain:
            return {sid: sid for sid in subject_ids}, []
        resolver = self.env["openspp.indicator.resolver"]
        mapped, unmapped = resolver.map_subjects_to_external(
            subject_model, subject_ids, fields_chain, required=required
        )
        return mapped, unmapped

    @api.model
    def enqueue_refresh(
        self, metric: str, subject_model: str, subject_ids: list[int], period_key: str, *, chunk_size: int = 2000
    ):
        """Enqueue background jobs (via queue_job if available) to refresh a metric for a set of subjects.

        Falls back to synchronous refresh if queue_job is not installed.
        """
        subject_ids = list({int(s) for s in subject_ids if s})
        if not subject_ids:
            return 0
        # Chunk ids
        chunks = [subject_ids[i : i + chunk_size] for i in range(0, len(subject_ids), chunk_size)]
        count = 0
        for chunk in chunks:
            try:
                # queue_job style delayed execution
                delayed = self.with_delay(
                    priority=20, identity_key=f"metric:{metric}:{period_key}:{hash(tuple(chunk))}"
                ).evaluate
                delayed(metric, subject_model, chunk, period_key, mode="refresh")
                count += 1
            except Exception:
                # Fallback to immediate refresh
                self.evaluate(metric, subject_model, chunk, period_key, mode="refresh")
                count += 1
        return count

    @api.model
    def enqueue_refresh_from_domain(
        self, metric: str, subject_model: str, domain: list[Any], period_key: str, *, chunk_size: int = 2000
    ):
        Model = self.env[subject_model]
        domain = list(domain or [])
        last_id = 0
        jobs = 0
        while True:
            batch_domain = domain + ([("id", ">", last_id)] if last_id else [])
            records = Model.search(batch_domain, limit=chunk_size, order="id")
            if not records:
                break
            batch_ids = [int(i) for i in records.ids]
            self.enqueue_refresh(metric, subject_model, batch_ids, period_key, chunk_size=chunk_size)
            jobs += 1
            last_id = batch_ids[-1]
            if len(batch_ids) < chunk_size:
                break
        return jobs
