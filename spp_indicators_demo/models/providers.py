from __future__ import annotations

import logging
import os
from typing import Any

import requests

from odoo import api

_logger = logging.getLogger(__name__)


class HouseholdSizeProvider:
    def compute_batch(self, env, ctx: dict[str, Any], subject_ids: list[int]) -> dict[int, Any]:
        Membership = env["g2p.group.membership"]
        rows = Membership.read_group([("is_ended", "=", False), ("group", "in", subject_ids)], ["group"], ["group"])
        counts = {r["group"][0]: r["group_count"] for r in rows if r.get("group")}
        return {int(sid): int(counts.get(sid, 0)) for sid in subject_ids}


class EducationAttendanceProvider:
    def compute_batch(self, env, ctx, subject_ids):
        ICP = env["ir.config_parameter"].sudo()
        base_url = (
            ICP.get_param("openspp_metrics.education.base_url")
            or os.environ.get("OPENSPP_EDU_BASE_URL")
            or "http://localhost:5001"
        )
        mapped = ctx.get("mapped_subjects") or {}
        ext_ids = []
        sid_index = []
        for sid in subject_ids:
            ext = mapped.get(sid)
            if ext:
                ext_ids.append(str(ext))
                sid_index.append(sid)
        if not ext_ids:
            return {}
        payload = {"period_key": str(ctx.get("period_key")), "subject_ids": ext_ids}
        url = base_url.rstrip("/") + "/metrics/attendance_pct"
        try:
            resp = requests.post(url, json=payload, timeout=5)
            resp.raise_for_status()
            data = resp.json() or {}
            results = data.get("results") or {}
        except Exception as e:
            _logger.warning("[openspp.metrics.demo] attendance provider error: %s", e)
            results = {}
        out = {}
        for sid, ext in zip(sid_index, ext_ids, strict=True):
            val = results.get(str(ext))
            if isinstance(val, int | float):
                out[int(sid)] = int(val)
        return out


def post_init_hook(cr, registry):
    env = api.Environment(cr, 1, {})
    _ensure_demo_definitions(env)
    _ensure_demo_credential(env)
    reg = env["openspp.indicator.registry"]
    # Register sample providers
    reg.register(
        name="household.size",
        handler=HouseholdSizeProvider(),
        return_type="number",
        subject_model="res.partner",
        capabilities={"supports_batch": True, "default_ttl": 0},
        provider="openspp_metrics_demo.household",
    )
    reg.register(
        name="education.attendance_pct",
        handler=EducationAttendanceProvider(),
        return_type="number",
        subject_model="res.partner",
        id_mapping={"fields": ["school_student_id", "external_id"], "required": False},
        capabilities={"supports_batch": True, "default_ttl": 86400},
        provider="openspp_metrics_demo.education",
    )


# Also register providers at import-time via static registry so they survive server restarts
try:  # pragma: no cover - defensive; safe if indicators not yet installed
    from odoo.addons.spp_indicators.models.metric_registry import register_static as _reg_static

    _reg_static(
        name="household.size",
        handler=HouseholdSizeProvider(),
        return_type="number",
        subject_model="res.partner",
        capabilities={"supports_batch": True, "default_ttl": 0},
        provider="openspp_metrics_demo.household",
    )
    _reg_static(
        name="education.attendance_pct",
        handler=EducationAttendanceProvider(),
        return_type="number",
        subject_model="res.partner",
        id_mapping={"fields": ["school_student_id", "external_id"], "required": False},
        capabilities={"supports_batch": True, "default_ttl": 86400},
        provider="openspp_metrics_demo.education",
    )
except Exception as e:
    _logger.info("[openspp.indicator.demo] Static registration skipped: %s", e)


def _ensure_demo_definitions(env):
    Definition = env["openspp.indicator.definition"].sudo()
    company = env.company
    demo_defs = [
        {
            "name": "household.size",
            "description": "Number of active members assigned to the household/group.",
            "subject_model": "res.partner",
            "value_type": "number",
            "period_granularity": "static",
            "default_ttl_seconds": 0,
        },
        {
            "name": "education.attendance_pct",
            "description": "Monthly attendance percentage reported by demo provider.",
            "subject_model": "res.partner",
            "value_type": "number",
            "period_granularity": "month",
            "default_ttl_seconds": 86400,
            "id_mapping_fields": "school_student_id,external_id",
            "id_mapping_required": False,
            "id_mapping_namespace": "demo_student",
        },
    ]
    for vals in demo_defs:
        existing = Definition.search(
            [
                ("name", "=", vals["name"]),
                ("company_id", "=", company.id),
            ],
            limit=1,
        )
        if existing:
            update_vals = {k: v for k, v in vals.items() if k not in ("name",)}
            existing.write(update_vals)
        else:
            vals = dict(vals)
            vals["company_id"] = company.id
            Definition.create(vals)


def _ensure_demo_credential(env):
    Credential = env["openspp.indicator.api_credential"].sudo()
    company = env.company
    name = "Demo OpenFn Token"
    existing = Credential.search([("name", "=", name), ("company_id", "=", company.id)], limit=1)
    if existing:
        return existing
    return Credential.create(
        {
            "name": name,
            "token_plain": "demo-token",
            "allowed_metric_pattern": "household.* ,education.* ,health.*",
            "status": "active",
            "company_id": company.id,
            "notes": "Demo credential for testing OpenFn integration flows. Token value: demo-token",
        }
    )
