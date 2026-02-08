from __future__ import annotations

import hashlib
import json
import re
from datetime import timedelta
from typing import Any

from odoo import fields, http
from odoo.exceptions import ValidationError
from odoo.http import request


class IndicatorsController(http.Controller):
    def _json(self, payload: dict[str, Any], status: int = 200):
        return request.make_json_response(payload, status=status)

    def _json_payload(self) -> dict[str, Any]:
        """Return the JSON payload for the current request as a dict.

        Routes in this controller are invoked via plain HTTP POST with a JSON
        body (not JSON-RPC). Starting with Odoo 17.4, ``request.jsonrequest`` is
        only populated for JSON-RPC dispatchers, so we manually parse the body
        and provide consistent error handling here.
        """
        try:
            data = request.get_json_data()
        except ValueError as err:
            raise ValidationError("Invalid JSON payload") from err
        if data is None:
            data = {}
        if data and not isinstance(data, dict):
            raise ValidationError("JSON payload must be an object at the top level")
        return data or {}

    def _hash_params(self, params: dict[str, Any]) -> str:
        payload = json.dumps(params, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha1(payload).hexdigest()

    def _infer_type(self, value: Any) -> str:
        if isinstance(value, int | float) and not isinstance(value, bool):
            return "number"
        if isinstance(value, str):
            return "string"
        return "json"

    def _authenticate(self, metric: str | None):
        token = request.httprequest.headers.get("X-Api-Key")
        env = request.env
        credential = None
        if token:
            credential = env["openspp.indicator.api_credential"].sudo().find_by_token(token)
            if not credential:
                return None, self._json({"error": "invalid_token"}, status=401)
            try:
                credential.check_active()
            except ValidationError as exc:
                return None, self._json({"error": "credential_inactive", "detail": str(exc)}, status=401)
            if metric and not credential.matches_metric(metric):
                return None, self._json({"error": "metric_not_allowed", "metric": metric}, status=403)
            try:
                credential.bump_usage(request.httprequest.remote_addr or "")
            except ValidationError as exc:
                return None, self._json({"error": "rate_limited", "detail": str(exc)}, status=429)
        else:
            user = env.user
            if not (user and user.has_group("base.group_system")):
                return None, self._json({"error": "missing_token"}, status=401)
        return credential, None

    def _validate_period_key(self, granularity: str, period_key: str) -> str | None:
        patterns = {
            "day": r"^\d{4}-\d{2}-\d{2}$",
            "week": r"^\d{4}-W\d{2}$",
            "month": r"^\d{4}-\d{2}$",
            "quarter": r"^\d{4}-(Q[1-4]|FY\d{2}-Q[1-4])$",
            "year": r"^\d{4}$",
            "cycle": r"^[\w:-]+$",
            "rolling": r"^rolling_(?:7d|14d|30d|60d|90d)$",
            "snapshot": r"^asof:\d{4}-\d{2}-\d{2}$",
            "static": r"^always$",
        }
        regex = patterns.get(granularity)
        if not regex:
            return None
        if not re.match(regex, period_key):
            return f"Period key `{period_key}` does not match required format for {granularity}."
        return None

    def _resolve_default_ttl(self, definition, provider_cfg) -> int:
        if provider_cfg and provider_cfg.default_ttl:
            return max(int(provider_cfg.default_ttl), 0)
        if definition.default_ttl_seconds:
            return max(int(definition.default_ttl_seconds), 0)
        param = request.env["ir.config_parameter"].sudo().get_param("openspp_metrics.default_ttl") or "0"
        try:
            return max(int(param), 0)
        except ValueError:
            return 0

    def _prepare_mapping_config(self, definition, provider_cfg) -> dict[str, Any]:
        cfg = definition.get_mapping_config().copy()
        if provider_cfg and provider_cfg.id_mapping_fields:
            cfg["fields"] = definition.normalize_mapping_fields(provider_cfg.id_mapping_fields)
            cfg["required"] = bool(provider_cfg.id_mapping_required)
        return cfg

    # Indicators API
    @http.route(["/api/indicators/push"], type="http", auth="none", methods=["POST"], csrf=False)
    def push(self, **kwargs):  # noqa: C901
        try:
            payload = self._json_payload()
        except ValidationError as exc:
            return self._json({"error": "invalid_json", "detail": str(exc)}, status=400)
        metric = payload.get("metric")
        if not metric:
            return self._json({"error": "missing_metric"}, status=400)
        credential, error = self._authenticate(metric)
        if error:
            return error
        # Choose company: explicit payload value, else credential company, else current
        company_id = payload.get("company_id") or (credential and credential.company_id.id) or request.env.company.id
        company = request.env["res.company"].browse(int(company_id))
        definition = (
            request.env["openspp.indicator.definition"]
            .with_company(company)
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
        if not definition:
            request.env["ir.logging"].sudo().create(
                {
                    "name": "openspp_metrics_push_missing_definition",
                    "type": "server",
                    "dbname": request.env.cr.dbname,
                    "level": "WARNING",
                    "message": f"definition not found metric={metric} company={company_id}",
                    "path": __name__,
                    "line": "0",
                    "func": "push",
                }
            )
            return self._json({"error": "unknown_metric", "metric": metric}, status=404)
        subject_model = payload.get("subject_model") or definition.subject_model
        if subject_model != definition.subject_model:
            return self._json(
                {
                    "error": "subject_model_mismatch",
                    "expected": definition.subject_model,
                    "received": subject_model,
                },
                status=400,
            )
        period_key = payload.get("period_key")
        if not period_key:
            return self._json({"error": "missing_period_key"}, status=400)
        period_error = self._validate_period_key(definition.period_granularity, period_key)
        if period_error:
            return self._json({"error": "invalid_period_key", "detail": period_error}, status=400)
        items = payload.get("items") or []
        if not isinstance(items, list) or not items:
            return self._json({"error": "invalid_items", "detail": "items must be a non-empty array."}, status=400)
        params = payload.get("params") or {}
        if params and not isinstance(params, dict):
            return self._json({"error": "invalid_params", "detail": "params must be a JSON object."}, status=400)
        # For cache friendliness we derive a deterministic params hash for non-empty params;
        # fallback to the empty hash so cache_only lookups without params still match.
        params_hash = payload.get("params_hash")
        if params_hash:
            params_hash = str(params_hash)
        elif params:
            params_hash = self._hash_params(params)
        else:
            params_hash = ""
        # Default provider label is "push" to align with tests and common usage.
        provider_label = payload.get("provider") or "push"
        errors_only = bool(payload.get("errors_only"))
        source_default = payload.get("source_ref")
        provider_cfg = (
            request.env["openspp.indicator.provider"]
            .with_company(company)
            .sudo()
            .search(
                [
                    ("metric", "=", metric),
                    ("name", "=", provider_label),
                ],
                limit=1,
            )
        )
        if not provider_cfg:
            provider_cfg = (
                request.env["openspp.indicator.provider"]
                .with_company(company)
                .sudo()
                .search([("metric", "=", metric)], limit=1)
            )
        mapping_cfg = self._prepare_mapping_config(definition, provider_cfg)
        namespace_expected = (mapping_cfg.get("namespace") or "").strip()
        external_type_default = payload.get("subject_external_id_type") or namespace_expected
        ttl_seconds = self._resolve_default_ttl(definition, provider_cfg)
        now_str = fields.Datetime.now()
        now_dt = fields.Datetime.to_datetime(now_str)
        resolver = request.env["openspp.indicator.resolver"].with_company(company).sudo()
        pending: list[dict[str, Any]] = []
        resolver_entries: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append({"index": idx, "code": "invalid_item", "message": "Item must be an object."})
                continue
            value = item.get("value")
            inferred_type = self._infer_type(value)
            if definition.value_type != "json" and inferred_type != definition.value_type:
                errors.append(
                    {
                        "index": idx,
                        "code": "value_type_mismatch",
                        "message": f"Expected value_type {definition.value_type}.",
                    }
                )
                continue
            entry = {
                "index": idx,
                "value": value,
                "value_type": item.get("value_type") or inferred_type,
                "coverage": item.get("coverage"),
                "as_of": item.get("as_of") or now_str,
                "expires_at": item.get("expires_at"),
                "source": item.get("source") or source_default or "push",
                "raw": item,
            }
            subject_id = item.get("subject_id")
            external_id = item.get("subject_external_id")
            external_type = item.get("subject_external_id_type") or external_type_default
            if subject_id:
                try:
                    entry["subject_id"] = int(subject_id)
                except (TypeError, ValueError):
                    errors.append(
                        {"index": idx, "code": "invalid_subject", "message": "subject_id must be an integer."}
                    )
                    continue
            elif external_id:
                if namespace_expected and external_type and external_type != namespace_expected:
                    errors.append(
                        {
                            "index": idx,
                            "code": "namespace_mismatch",
                            "message": f"Expected namespace `{namespace_expected}`.",
                        }
                    )
                    continue
                entry["external_id"] = external_id
                resolver_entries.append({"index": idx, "external_id": external_id})
            else:
                errors.append(
                    {
                        "index": idx,
                        "code": "missing_subject",
                        "message": "subject_id or subject_external_id is required.",
                    }
                )
                continue
            if not entry["expires_at"] and ttl_seconds:
                entry["expires_at"] = fields.Datetime.to_string(now_dt + timedelta(seconds=ttl_seconds))
            pending.append(entry)
        if resolver_entries:
            mapped, mapping_errors = resolver.resolve_external_ids(
                subject_model,
                resolver_entries,
                mapping_cfg.get("fields") or [],
                required=bool(mapping_cfg.get("required")),
            )
            errors.extend(mapping_errors)
            for entry in pending:
                if entry.get("subject_id"):
                    continue
                idx = entry["index"]
                if idx in mapped:
                    entry["subject_id"] = mapped[idx]
        entry_by_index = {entry["index"]: entry for entry in pending}
        rows: list[dict[str, Any]] = []
        for entry in pending:
            if not entry.get("subject_id"):
                errors.append(
                    {"index": entry["index"], "code": "mapping_failed", "message": "Unable to resolve subject."}
                )
                continue
            rows.append(
                {
                    "metric": metric,
                    "provider": provider_label,
                    "subject_model": subject_model,
                    "subject_id": entry["subject_id"],
                    "period_key": period_key,
                    "value_json": entry["value"],
                    "value_type": entry["value_type"],
                    "params_hash": params_hash,
                    "coverage": entry.get("coverage"),
                    "as_of": entry.get("as_of"),
                    "fetched_at": now_str,
                    "expires_at": entry.get("expires_at"),
                    "source": entry.get("source"),
                    "company_id": company_id,
                }
            )
        result = {"inserted": 0, "updated": 0}
        if rows and not errors_only:
            fv = request.env["openspp.indicator.value"].with_company(company).sudo()
            result = fv.upsert_values(rows)
            # Normalize provider label if older rows exist with empty provider
            if provider_label:
                try:
                    q = fv.env.cr
                    ids = [int(r.get("subject_id")) for r in rows]
                    q.execute(
                        """
                        UPDATE openspp_indicator_value
                           SET provider = %s
                         WHERE company_id = %s AND metric = %s AND subject_model = %s
                           AND period_key = %s AND params_hash = %s AND provider = ''
                           AND subject_id = ANY(%s)
                        """,
                        (provider_label, company_id, metric, subject_model, period_key, params_hash or "", ids),
                    )
                except Exception:
                    # best-effort; ignore if table not yet present during init
                    pass
        error_model = request.env["openspp.indicator.push.error"].with_company(company).sudo()
        for err in errors:
            payload_item = (
                entry_by_index.get(err.get("index"), {}).get("raw") if err.get("index") in entry_by_index else None
            )
            error_model.log_error(
                metric,
                err.get("code") or "push_error",
                err.get("message") or "",
                credential=credential,
                payload=payload_item,
                subject_ref=(entry_by_index.get(err.get("index")) or {}).get("external_id")
                or str((entry_by_index.get(err.get("index")) or {}).get("subject_id") or ""),
            )
        # Debug/log context for troubleshooting provider/params storage
        first_provider = rows[0]["provider"] if rows else provider_label
        first_phash = rows[0]["params_hash"] if rows else params_hash
        request.env["ir.logging"].sudo().create(
            {
                "name": "openspp_metrics_push",
                "type": "server",
                "dbname": request.env.cr.dbname,
                "level": "INFO",
                "message": (
                    f"push metric={metric} provider={first_provider} phash={first_phash} "
                    f"inserted={result['inserted']} updated={result['updated']} "
                    f"errors={len(errors)} dry_run={int(errors_only)} company_id={company_id}"
                ),
                "path": __name__,
                "line": "0",
                "func": "push",
            }
        )
        unmapped_count = sum(1 for err in errors if str(err.get("code", "")).startswith("mapping"))
        return self._json(
            {
                "ok": True,
                "metric": metric,
                "period_key": period_key,
                "inserted": result["inserted"],
                "updated": result["updated"],
                "processed": len(rows),
                "errors": errors,
                "unmapped_subjects": unmapped_count,
                "dry_run": errors_only,
            }
        )

    @http.route(["/api/indicators/invalidate"], type="http", auth="none", methods=["POST"], csrf=False)
    def invalidate(self, **kwargs):
        try:
            payload = self._json_payload()
        except ValidationError as exc:
            return self._json({"error": "invalid_json", "detail": str(exc)}, status=400)
        metric = payload.get("metric")
        if not metric:
            return self._json({"error": "missing_metric"}, status=400)
        credential, error = self._authenticate(metric)
        if error:
            return error
        company_id = payload.get("company_id") or (credential and credential.company_id.id) or request.env.company.id
        definition = (
            request.env["openspp.indicator.definition"]
            .with_company(request.env["res.company"].browse(int(company_id)))
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
        if not definition:
            return self._json({"error": "unknown_metric", "metric": metric}, status=404)
        subject_model = payload.get("subject_model") or definition.subject_model
        if subject_model != definition.subject_model:
            return self._json({"error": "subject_model_mismatch", "expected": definition.subject_model}, status=400)
        period_key = payload.get("period_key")
        subject_ids = payload.get("subject_ids") or []
        subject_external_ids = payload.get("subject_external_ids") or []
        # Default provider label aligned with push default
        provider_label = payload.get("provider") or "push"
        params_hash = payload.get("params_hash") or ""
        mapping_cfg = self._prepare_mapping_config(
            definition,
            request.env["openspp.indicator.provider"]
            .with_company(request.env["res.company"].browse(int(company_id)))
            .sudo()
            .search(
                [
                    ("metric", "=", metric),
                    ("name", "=", provider_label),
                ],
                limit=1,
            ),
        )
        resolver = (
            request.env["openspp.indicator.resolver"]
            .with_company(request.env["res.company"].browse(int(company_id)))
            .sudo()
        )
        errors = []
        if subject_external_ids and isinstance(subject_external_ids, list):
            resolver_entries = [{"index": idx, "external_id": ext} for idx, ext in enumerate(subject_external_ids)]
            mapped, mapping_errors = resolver.resolve_external_ids(
                subject_model,
                resolver_entries,
                mapping_cfg.get("fields") or [],
                required=bool(mapping_cfg.get("required")),
            )
            errors.extend(mapping_errors)
            ordered = [mapped[idx] for idx in sorted(mapped.keys())]
            subject_ids.extend(ordered)
        subject_ids = list({int(sid) for sid in subject_ids if sid})
        request.env["openspp.indicator.value"].with_company(
            request.env["res.company"].browse(int(company_id))
        ).sudo().invalidate(
            metric,
            subject_model,
            period_key or None,
            subject_ids or None,
            provider=provider_label,
            params_hash=params_hash,
            company_id=company_id,
        )
        request.env["ir.logging"].sudo().create(
            {
                "name": "openspp_metrics_invalidate",
                "type": "server",
                "dbname": request.env.cr.dbname,
                "level": "INFO",
                "message": (
                    f"invalidate metric={metric} period={period_key} "
                    f"count={(len(subject_ids) if subject_ids else 'ALL')}"
                ),
                "path": __name__,
                "line": "0",
                "func": "invalidate",
            }
        )
        return self._json(
            {
                "ok": True,
                "invalidated_subjects": len(subject_ids) if subject_ids else None,
                "errors": errors,
            }
        )
