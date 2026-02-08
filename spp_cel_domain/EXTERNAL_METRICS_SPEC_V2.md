# External Metrics for OpenSPP/OpenG2P — Final Spec (V2)

Date: 2025-10-01 Owner: OpenSPP CEL Team Status: Final for implementation hand‑off (V2) Targets: Odoo 17
(OpenSPP + OpenG2P)

Summary

- Introduces a platform‑wide metrics capability (module name: `openspp_metrics`) usable from CEL, registry
  lists, and reports.
- Keeps the user DSL simple, explicit, and non‑magical. No hidden defaults that change truth.
- Scales to millions of subjects with batching, caching, and optional provider push ingestion.

---

## 1. Goals & Non‑Goals

Goals

- Simple DSL for non‑developers to reference external metrics in CEL and UI.
- Deterministic semantics (unknown, coverage, freshness) with clear Explain output.
- Pluggable provider contract (pull + optional push), robust ID mapping, and cache invalidation.
- Scale to large datasets without N×1 calls; support precompute when justified.

Non‑Goals (V2)

- Cross‑tenant federation and streaming change data capture.
- Provider‑specific UI beyond Explain and admin wizards.

---

## 2. Architecture Overview

Modules

- `openspp_metrics` (new core)
  - Owns feature store, provider registry, push/pull APIs, invalidation, admin dashboards.
  - Exposes Odoo models: `openspp.indicator.registry`, `openspp.function.registry`, `openspp.feature.store`.
- `cel_domain` (existing)
  - Soft‑depends at runtime; uses the registries to evaluate metrics in CEL expressions.
- Reuse elsewhere
  - Registry list views may show columns backed by `openspp.feature.store`.
  - Reporting/exports can query the feature store directly.

---

## 3. DSL (User‑Facing)

3.1 Namespaced metric functions (primary)

- Examples
  - `education.attendance_pct(period[, for=subject]) -> number 0..100`
  - `health.vaccination_status(period[, for=subject]) -> string/boolean`
  - `finance.poverty_score(params..., [for=subject]) -> number`
- `for` defaults to the current symbol (e.g., `me` or loop variable `m`).
- `period` accepts a calendar period or a `g2p.cycle` (see §4).

  3.2 Catalog function (escape hatch)

- `metric("education.attendance_pct", within=last_month(), for=m, mode="fallback", max_staleness="P30D")`

  3.3 Aggregation helpers for collections

- `avg_over(members, education.attendance_pct(last_month(), for=m))`
- `all_over(members, education.attendance_pct(last_month(), for=m) >= 85)`
- `coverage_over(members, education.attendance_pct(last_month(), for=m))`

  3.4 Non‑magic defaults

- Unknowns are excluded from numeric aggregates; booleans fail‑closed (unknown → false).
- No implicit coverage gating. If coverage matters, authors wrap with `require_coverage(expr, min=0.8)`.

Examples

- Child with good attendance last month:
  `members.exists(m, age_years(m.birthdate) < 5 and education.attendance_pct(last_month(), for=m) >= 85)`
- Catalog style with cycles: see §4 + §13 examples.

---

## 4. Periods & Cycles (OpenG2P‑aligned)

Cycles use g2p.cycle (fields: name, program_id, start_date, end_date, sequence, state).

Helpers

- `cycle_id(id)` — fetch exact cycle by DB id.
- `cycle(program, name=...)` — cycle for a program and unique name.
- `last_cycle(program, states=("approved","distributed","ended"))` — highest sequence.
- `first_cycle(program, states=None)` — lowest sequence.
- `previous(c)` / `next(c)` — navigate by sequence within the same program.

Usage

- When a cycle is passed to a metric, it is converted to `Period(c.start_date, c.end_date)`.
- The UI may provide a `cycle_id` in context, but metrics only use a cycle when referenced explicitly (no
  implicit defaults).

As‑of (freeze) semantics

- Default snapshot time: `c.approved_date` when set; else provider’s `freeze_lag` capability may use
  `c.end_date + lag`; else “now”.

---

## 5. Evaluation Context (passed to helpers/providers)

Fields

- Execution: `mode` (preview|evaluate), `request_id`, `deadline_ms`, `tenant_id`, `company_id`, `user_id`,
  `timezone`.
- Query: `profile` (individuals|groups|program_memberships|entitlements), `root_model`, `program_id`, optional
  `cycle_id`.
- Subject: `subject_model`, `subject_ids` (batched), `id_mapping` (field chain; §6.4).
- Freshness: `cache_mode` (cache_only|refresh|fallback), `max_staleness` (ISO 8601 duration), `min_coverage`
  (for Explain warnings), `sample_limit`.
- Limits: `batch_size`, `max_concurrency`, `timeout_ms`, `retry` policy.

Preview vs Evaluate

- Preview uses `cache_mode=fallback`, tight deadlines, no blocking refresh.
- Evaluate may refresh and run as a background job if needed.

---

## 6. Provider Contract

6.1 Registration (soft dependency)

- Providers register metrics in `post_init_hook` only if `openspp.indicator.registry` exists.
- Example

```
# spp_education/__init__.py
from odoo import api, SUPERUSER_ID

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    if 'openspp.indicator.registry' not in env:
        return
    from .providers.attendance import AttendanceProvider
    env['openspp.indicator.registry'].register(
        name='education.attendance_pct',
        handler=AttendanceProvider(),
        return_type='number',
        subject_model='res.partner',
        id_mapping={'strategy': 'field_chain', 'fields': ['school_student_id', 'external_id'], 'required': True},
        capabilities={
            'supports_batch': True,
            'max_batch_size': 5000,
            'recommended_concurrency': 4,
            'cost_hint': 'med',
            'staleness_tolerance': 'P1D',
            'default_ttl': 86400,
            'push_enabled': True,
        }
    )
```

6.2 Batch API (pull)

- `compute_batch(ctx, subject_ids, period, params) -> {id: BatchResult}`
- BatchResult: `{value|None, dtype, coverage|None, as_of|None, meta|None, error|None}`

  6.3 Optimizer hints (optional)

- Pushdowns (e.g., `school_id`), grouping keys for sharding, cost class.

  6.4 Subject ID mapping (robust)

- Config

```
id_mapping:
  strategy: field_chain
  fields: ["school_student_id", "external_id", "national_id"]
  allow_internal_fallback: false
  required: true
```

- Unmapped subjects produce `error=NO_EXTERNAL_ID` (unknown); no guessing.

  6.5 Push ingestion (optional)

- Endpoint: `POST /api/metrics/push` with `Authorization` and `X-Idempotency-Key`.
- Payload includes `provider`, `metric`, `subject_model`, `period_key` (`g2p.cycle:<id>` or
  `dates:YYYY-MM-DD..YYYY-MM-DD`), and `points` [{external_id|subject_id, value, dtype, as_of, coverage?,
  expires_at?, meta?}].
- Idempotent, last‑writer‑wins by `as_of`. Supports NDJSON/file ingestion in Phase 2.

---

## 7. Execution & Semantics

7.1 Planner

- Apply cheap local domains first to shrink candidate sets.
- For relations (`exists`/`count`), compute child IDs via local child predicates; if empty → short‑circuit to
  no parents.
- Group metric requests by `(provider, metric, period_key, params_hash)` and call providers in micro‑batches
  with bounded concurrency.

  7.2 Unknown/coverage/freshness

- Unknown: boolean filters fail‑closed; numeric comparisons do not match.
- Coverage: no implicit gating; expose via `coverage_over` and Explain. Optional `require_coverage(expr, min)`
  gate in DSL.
- Freshness modes: `cache_only`, `refresh`, `fallback` (preview returns cache and enqueues refresh when
  stale).

---

## 8. Feature Store & Caching (openspp_metrics)

8.1 Table (logical)

```
openspp_feature_value(
  id PK,
  provider text,
  metric text,
  subject_model text,
  subject_id bigint,
  period_key text,            -- dates:YYYY-MM-DD..YYYY-MM-DD or g2p.cycle:<id>
  params_hash text,
  dtype text,
  value jsonb,
  coverage real,
  source text,                -- 'pull'|'push'
  fetched_at timestamptz,
  as_of timestamptz,
  expires_at timestamptz,
  error_code text,
  error_message text,
  meta jsonb,
  company_id int
)
UNIQUE(provider, metric, subject_model, subject_id, period_key, params_hash, company_id)
```

Partition & indexes

- Phase 1b/1c: PARTITION BY HASH(subject_id) with 16 partitions; indexes on
  `(provider, metric, subject_model, subject_id, period_key)` and `(provider, metric, period_key)`.
- Phase 3: optional composite RANGE(period_key) + HASH(subject_id).

  8.5 Caching layers

- In‑request memo: per evaluation pass, dedupes repeated lookups within one request.
- Worker LRU cache: small TTL (minutes) to smooth repeated previews without hitting DB or providers.
- Persistent feature store: openspp_feature_value (above) with TTL/expiry.

  8.2 Freshness

- `expires_at = fetched_at + default_ttl` unless restricted by `max_staleness`.

  8.3 Invalidation

- Provider push invalidation: mark stale by `(metric, subject_ids, period_key)`.
- Admin wizard: expire by tenant/company, program/cycle or date range.
- Epoch bump (advanced): provider increases `data_epoch` to expire cohorts.

  8.4 Push ingestion

- Stored with `source='push'`, prefer freshest non‑expired row regardless of source.

---

## 9. Scale & Precompute

- Micro‑batches (2–10k), tuned concurrency; token‑bucket rate limiting per provider.
- Precompute nightly and on cycle rollover for hot windows (e.g., last_month school‑age cohort).
- Heuristics to suggest precompute: queries/day > 100, avg latency > 1s, cache hit < 60%.

---

## 10. UX & Explain (API shape)

Explain includes (implemented subset)

- execution_mode, request_id (added), duration_ms (future)
- metrics: subjects_requested, cache_hits/misses, fresh_fetches, coverage (implemented)
- warnings (added): LOW_COVERAGE (<0.8), CACHE_MISSES (>0)
- Wizard shows a concise text; structured metrics + request_id are returned in explain_struct

User/Admin actions (in UI)

- Prefetch now: enqueue a job to refresh metrics for the current candidate set/period.
- Run exact as job: re‑evaluate with `mode=evaluate` (allow refresh) when previews use cache/fallback.
- Adjust freshness/coverage: per‑run overrides for `cache_mode`, `max_staleness`, and `require_coverage`
  threshold.

---

## 11. Security, Governance & Audit

Security

- Authentication for push/invalidation: OAuth2 client credentials or HMAC signatures; optional IP allowlist.
- Access control: provider usage and admin screens guarded by dedicated access groups.
- Secrets: credentials in `ir.config_parameter` or secret store; never hard‑coded.

Governance & Privacy

- Data minimization: store only needed features; allow value bucketing/rounding or hashing as required.
- Multi‑tenant isolation: all rows carry `company_id`; endpoints and queries are scoped to company/tenant.

Audit & Observability

- Audit logs: who, when, provider, metric, #subjects, period_key, mode (pull/push), outcome, and request_id.
- Metrics: request counts, latency, cache hit ratio, coverage distribution, error rates; dashboards for
  operators.
- Bitemporal metadata: persist both `as_of` (provider data time) and `fetched_at` (retrieval time).

---

## 12. Configuration & Admin Controls

Per‑provider settings (system parameters or model records)

- Endpoint/base URL and auth (OAuth2/HMAC secrets)
- default_ttl, staleness_tolerance, optional freeze_lag
- max_batch_size, recommended_concurrency, timeouts, retries/backoff
- id_mapping field chain (e.g., [school_student_id, external_id, national_id]) and allow_internal_fallback

Global/admin settings

- Approximate previews (off by default)
- UI warnings threshold for coverage (does not change truth)
- Prefetch schedules for hot periods (e.g., last_month()) and cohorts

---

## 13. Testing & Rollout Plan

Phase 1a (PoC)

- `metric()` + `period()` only; in‑memory cache_only; stub provider; small tests (~100 partners).

Phase 1b (MVP)

- Full `metric(...)` + `last_month()`; CelContext; feature store (HASH partitions); refresh/fallback;
  id‑mapping field_chain; provider push (small JSON); Explain basics.

Phase 1c (Production)

- Micro‑batching, concurrency caps, backpressure; REST invalidation + NDJSON/file push; require_coverage();
  planner optimization; admin dashboards; precompute heuristics.

---

## 14. Integration with OpenSPP “Indicators”

Background

- In `g2p_registry_membership/models/group.py`, groups have stored, computed “indicator” fields (e.g.,
  `z_ind_grp_num_individuals`) maintained via jobs.

Approach

- Keep indicators for intra‑Odoo aggregates (fast SQL across group memberships).
- Use `openspp_metrics` for external or heavy features. Two options to expose in UI:
  1. Virtual: compute at view time via `openspp.feature.store` reads.
  2. Materialized: add stored computed fields that pull from the feature store and schedule recompute jobs
     (mirrors existing indicator pattern).

Benefit

- Unified, audited source for metrics while preserving the indicator UX patterns admins already know.

---

## 15. Examples

Individuals

```
# Vaccination due last month
health.vaccination_status(last_month()) == "due"

# Poverty score in last 12 months >= 45
finance.poverty_score(period(months_ago(12).start, today())) >= 45
```

Groups

```
# Single woman‑headed HH with a child under 5 with 85%+ attendance
count(members, m, head(m)) == 1 and
members.exists(m, head(m) and m.gender == "Female") and
members.exists(m, age_years(m.birthdate) < 5 and education.attendance_pct(last_month(), for=m) >= 85)
```

Catalog + cycles

```
metric(
  "education.attendance_pct",
  within=previous(last_cycle(program("Edu Program"))),
  for=m,
  mode="fallback",
  max_staleness="P30D",
  min_coverage=0.9
) >= 85
```

---

## 16. Decisions (for implementers)

- last_cycle default states = (approved, distributed, ended); first_cycle no state filter.
- No implicit coverage gating in evaluation; use require_coverage or admin UI warnings.
- No “current_cycle” helper to avoid ambiguity; use last/first/previous/next explicitly.
- Module name = `openspp_metrics`.

---

## 17. Open Items (minor)

- Any additional Explain fields later (e.g., tenant label) can be added without changing semantics.
- Provider freeze_lag defaults per provider; document alongside provider config.

---

End of V2 Spec

---

# Addendum — Implementation Progress (2025‑10‑02)

This repository now ships Phase 1 fully and key Phase 2 items:

- New addon `openspp_metrics`

  - Feature store model/table: `openspp.indicator.value`.
    - Columns now include: `metric`, `provider`, `subject_model`, `subject_id`, `period_key`, `value_json`,
      `value_type`, `params_hash`, `coverage`, `as_of`, `fetched_at`, `expires_at`, `source`, `error_code`,
      `error_message`, `updated_at`, `company_id`.
    - Unique key: `(metric, provider, subject_model, subject_id, period_key, params_hash, company_id)`.
  - Registry: `openspp.indicator.registry` (Python‑backed) + `register_static()` for deterministic startup.
  - Service: `openspp.metrics.evaluate()` with cache_only/refresh/fallback, ID mapping chain, and stats
    (requested/hits/misses/fresh/coverage).
  - HTTP: `POST /api/metrics/push`, `POST /api/metrics/invalidate` (X‑Api‑Key or admin session).
  - Access rules: admin R/W, users read‑only.

- CEL integration (`cel_domain`)

  - DSL: `metric(name, subject, period_key)` and namespaced metric functions (e.g.,
    `education.attendance_pct(period?, for?)`).
  - Cycle helpers: `cycle`, `last_cycle`, `first_cycle`, `previous`, `next`.
  - Executor Explain includes concise per‑metric stats in preview and a structured metrics panel in the
    wizard.
  - Correct exists/count short‑circuiting and membership splitting.

- Providers

  - Built‑in: `household.size` (active members) registered statically.

- Tests
  - Integration tests for metric() and push flow; Doodba tasks updated; full suite green.

## Sample external service (education.attendance_pct)

We include a repeatable Flask service for development and demos.

Location: `tools/mock_services/attendance_pct_service.py`

Run:

```
python tools/mock_services/attendance_pct_service.py --host 0.0.0.0 --port 5001
```

Endpoint:

```
POST /metrics/attendance_pct
{
  "period_key": "2024-09",
  "subject_ids": ["EXT123", "EXT999"]
}

Response:
{
  "results": { "EXT123": 88, "EXT999": 74 }
}
```

Values are deterministic using a hash of `subject_id + period_key`.

Odoo provider (pull) registers `education.attendance_pct` and reads base URL from:
`ir.config_parameter['openspp_metrics.education.base_url']` (e.g., `http://localhost:5001`).

Use in CEL:

```
metric("education.attendance_pct", me, "2024-09") >= 85
```

## Phase 2 — Implemented now

1. Partitioning & indexes

- `openspp_feature_value` is created PARTITION BY HASH(subject_id) with helper to create 16 partitions, plus
  indexes on `(metric, subject_model, subject_id, period_key)` and `(metric, period_key)`.

2. Background jobs & micro‑batching (initial)

- `openspp.metrics.enqueue_refresh(metric, subject_model, ids, period_key, chunk_size=2000)` enqueues refresh
  via `queue_job` when available, falling back to immediate refresh.

3. Rich Explain & UI

- `compile_and_preview` returns `explain_struct.metrics` and the wizard renders a tabular list of per‑metric
  stats.

4. Provider config UI

- `res.config.settings` fields to manage base URL and a global default TTL.

Next Phase 2 items queued

- Coverage helpers (`require_coverage`, `coverage_over/all_over/avg_over`) and a precompute wizard; these
  remain planned but not yet implemented to keep scope focused.
