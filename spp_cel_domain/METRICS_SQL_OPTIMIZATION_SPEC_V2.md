# CEL Metrics SQL Optimization — V2 (Odoo 17)

Date: 2025-10-02 Status: Ready for implementation Modules: `openspp_metrics`, `openspp_cel/cel_domain`

---

## Executive Summary

Goal: Make CEL expressions that compare metric values (e.g.,
`metric("education.attendance_pct", me, "2024-09") >= 85`) fast and memory‑safe on large datasets, without
bypassing Odoo record rules or returning stale/partial data.

Strategy: Two-tier execution

- Tier 1 — SQL Fast Path: Build an `INSELECT` domain against `openspp_feature_value` to let Postgres filter
  candidates with indexes, zero Python materialization of ID lists, and full record-rule enforcement.
- Tier 2 — Async Refresh: When cache is incomplete/stale or dataset is too large, never block in preview; in
  evaluate mode enqueue background refresh jobs and return once cached.

Key constraints adopted in V2

- No partial indexes using `NOW()`; use stable composite indexes that work with partitions and the planner.
- All user-facing queries keep Odoo record rules by using domains; no direct SQL joins for subject tables.
- Preview never calls external providers (cache-only); evaluate may enqueue refresh via `queue_job`.

---

## Scope (V2)

Covered

- Subject-level metric comparisons on the current model (e.g., partners, groups): numeric and equality
  operators.
- Cache completeness/freshness preflight; SQL fast path when fresh and complete.
- Async refresh queueing in evaluate mode; clear messaging in preview.
- Index additions, flags, and targeted tests.

Deferred (remain in Python for now)

- Aggregators over relations: `avg_over`, `coverage_over`, `all_over`.
- Multi-metric SQL fusion (`metric A AND metric B` in one SQL) — future enhancement.

---

## Current Baseline (as of V2)

Data model: `openspp_feature_value` (JSONB value, keys: `metric`, `provider`, `subject_model`, `subject_id`,
`period_key`, `params_hash`, `company_id`, plus `coverage`, `as_of`, `fetched_at`, `expires_at`, `error_*`).

Indexes already present

- `idx_ofv_metric_subject_period(company_id, metric, provider, subject_model, subject_id, period_key, params_hash)`
- `idx_ofv_metric_period(company_id, metric, period_key)`
- `idx_ofv_provider(company_id, provider)`

Partitioning: HASH(subject_id) with N=16 partitions created automatically on install.

Executor baseline: `_exec_metric` loads candidate IDs in Python then calls
`openspp.metrics.evaluate(..., mode='fallback')`, filters in Python. This causes full scans and high memory on
100k+ cohorts.

---

## V2 Design

### 1) Preview vs Evaluate semantics

- Preview (`cel_mode=preview`, used by Compile & Preview UI):

  - Never call providers; use cache-only.
  - If cache not fresh/complete for the cohort, do not fall back to Python refresh. Return a clear
    explain/warning and (optionally) a UI affordance to queue refresh.

- Evaluate (non-preview, e.g., batch/back-end):
  - If cache not fresh/complete and dataset ≥ threshold, enqueue refresh jobs and return (or short-circuit)
    based on feature flag. No silent truncation.

### 2) Cache preflight checker (cheap SQL)

For a given subject model `M`, metric `m`, period `p`, provider `prov`, params_hash `ph`, company `c`, and
base domain `D`:

- Compute `base_count` = count of distinct records in `M` that satisfy `D` (via standard `search_count(D)`).
- Compute `have_count` = count of distinct IDs in `M` with
  `id IN (SELECT subject_id FROM openspp_feature_value WHERE company_id=c AND metric=m AND subject_model=M AND period_key=p AND provider=prov AND params_hash=ph AND error_code IS NULL)`.
- Compute `stale_count` = count of distinct IDs with
  `id IN (SELECT subject_id ... WHERE (expires_at IS NOT NULL AND expires_at <= NOW()) )`.

Status rules

- `fresh_and_complete` when `have_count == base_count` and `stale_count == 0`.
- `incomplete` when `have_count < base_count`.
- `stale` when `stale_count > 0`.

Implementation notes

- Use parametrized SQL in a helper; keep it read-only.
- If `base_count` ≥ `cel.async_threshold`, treat as “large cohort”.

### 3) SQL fast path via SQL domain

When status is `fresh_and_complete` and the comparison is supported, build a domain that embeds the feature
store predicate:

Domain structure

- Final domain = `AND(D, ('id', 'in', SQL(...)))`
- Odoo will apply record rules on `M` because `search()` still runs on `M`.

SQL template (numeric compare)

```sql
SELECT DISTINCT fv.subject_id
FROM openspp_feature_value fv
WHERE fv.company_id = %(company_id)s
  AND fv.metric = %(metric)s
  AND fv.subject_model = %(subject_model)s
  AND fv.period_key = %(period_key)s
  AND fv.provider = %(provider)s
  AND fv.params_hash = %(params_hash)s
  AND fv.error_code IS NULL
  AND (fv.expires_at IS NULL OR fv.expires_at > NOW())
  AND jsonb_typeof(fv.value_json) = 'number'
  AND (fv.value_json::numeric) %(op)s %(rhs)s
```

SQL template (string equality/inequality)

```sql
... AND fv.value_json::text %(op)s %(rhs_text)s
```

Supported operators in V2

- Numeric: `==`, `!=`, `>`, `>=`, `<`, `<=`
- String: `==`, `!=` (other string ops can be added later; prefer exact matches in V2)

Null/missing/error handling

- Rows with `error_code` are excluded.
- `NULL` values do not match any predicate (safest default).

Type safety

- Guard with `jsonb_typeof(value_json) = 'number'` before numeric casts.

### 4) Evaluate mode and async refresh

Evaluate behavior (non-preview):

- If status != `fresh_and_complete`:
  - If `base_count >= cel.async_threshold` → enqueue refresh (`openspp.metrics.enqueue_refresh`) in
    micro-batches; return explain with job count.
  - Else (small cohort): call `openspp.metrics.evaluate(..., mode='refresh')` synchronously to fill cache,
    then immediately execute the SQL fast path.

Queue details (existing API)

- Use `with_delay(priority=20, identity_key=...)` when `queue_job` is available; fallback to immediate refresh
  if not.
- Chunk size: `ir.config_parameter['cel.chunk_size']` (default 10000).

### 5) Provider/params resolution

- Provider label comes from `openspp.indicator.registry.get(metric)['provider']` if present; fallback to
  `metric`.
- `params_hash` should be `""` for CEL V2 unless the CEL translator passes explicit params; keep code ready to
  accept it.

### 6) Indexing plan

Add a subject-first composite index (safe with partitions and planner):

```sql
CREATE INDEX IF NOT EXISTS idx_ofv_subject_company_metric_period
ON openspp_feature_value (subject_id, company_id, metric, subject_model, period_key, provider, params_hash);
```

Keep others as-is. Do NOT create partial indexes with `NOW()`.

### 7) Feature flags (ir.config_parameter)

- `cel.enable_sql_metrics` (default `true`): master switch for SQL fast path.
- `cel.preview_cache_only` (default `true`): in preview, never call providers.
- `cel.async_threshold` (default `50000`): cohort size threshold to force async.
- `cel.chunk_size` (default `10000`): micro-batch size for refresh.

---

## Implementation Guide (file-level tasks)

### A) Feature store indexes

File: `openspp_metrics/models/feature_store.py`

- Function `_ensure_indexes()` — add:
  ```python
  cr.execute(
      "CREATE INDEX IF NOT EXISTS idx_ofv_subject_company_metric_period "
      "ON openspp_feature_value (subject_id, company_id, metric, subject_model, period_key, provider, params_hash)"
  )
  ```

### B) Executor: preview gating, preflight, SQL fast path

File: `cel_domain/models/cel_executor.py`

1. Preview gating in `_exec_metric`

   - Read `cel_mode` from context; if `preview`, set service mode to `cache_only` for any evaluate calls.

2. Add helper `_metric_registry_info(metric) -> (provider, return_type)`

   - Query `openspp.indicator.registry.get(metric)`; default provider to metric name.

3. Add helper
   `_metric_cache_status_sql(model, base_domain, metric, period_key, provider, params_hash) -> dict`

   - Compute `base_count`, `have_count`, `stale_count` as described above using parametrized SQL `INSELECT` on
     `openspp_feature_value`.
   - Return `{'status': 'fresh'|'stale'|'incomplete', 'base': n, 'have': n, 'stale': n}`.

4. Add helper
   `_metric_inselect_sql(model, metric, period_key, provider, params_hash, op, rhs, value_type) -> (sql, params)`

   - Build one of the two SQL templates (numeric or string).
   - Map CEL ops to SQL ops; enforce `error_code IS NULL` and freshness.

5. Rewrite `_exec_metric`

   - Resolve provider/params.
   - Read flags/thresholds.
   - Call preflight.
   - If `enable_sql_metrics` and status is fresh+complete and operator/type supported:
     - Build `('id', 'inselect', (sql, params))` domain; return `search()` IDs.
   - Else (preview): append explain warning and return `[]` (or fall back to cache-only + Python filter behind
     optional flag, default disabled in V2).
   - Else (evaluate): if `base_count >= async_threshold` enqueue refresh; else call
     `evaluate(..., mode='refresh')` and retry SQL path.

6. Explain
   - Enrich `metrics_info` with `{path: 'sql'|'python'|'queued'|'cache_only', status, base, have, stale}`.

### C) No change to aggregators in V2

Keep `_exec_agg_metric` as-is. Document that aggregators stay in Python. Future V3 may add SQL GROUP BY over
through models.

---

## Testing Plan

Unit tests (fast)

- `TestMetricFastPathNumeric`: seed `openspp_feature_value` for N partners; assert that `>=, >, <=, <, ==, !=`
  match expected IDs via SQL path. Verify `metrics_info.path == 'sql'`.
- `TestMetricFastPathString`: seed string values; assert equality/inequality behavior.
- `TestMetricPreflightStatus`: construct cases for fresh, stale, incomplete and assert returned status.

Integration tests (targeted)

- Preview gating: with missing cache, `compile_and_preview` returns `count==0`, explain contains
  “LOW_COVERAGE/CACHE_MISSES”, and `metrics_info.path == 'cache_only'`.
- Evaluate small cohort: missing cache -> refresh -> SQL path -> IDs correct in one call.
- Evaluate large cohort: `base_count >= async_threshold` -> enqueue refresh; ensure no provider calls made
  inline; explain marks `queued`.

Security tests

- Create a partner record rule limiting visibility; ensure `search()` with INSELECT does not breach the rule
  (IDs returned are a subset of visible ones).

Performance sanity (optional dev test)

- Seed 50k partners + cached numeric metric; measure search time < 500ms on dev laptop with warm cache.

---

## Configuration & Rollout

System parameters (defaults)

- `cel.enable_sql_metrics=true`
- `cel.preview_cache_only=true`
- `cel.async_threshold=50000`
- `cel.chunk_size=10000`

Rollout steps

1. Deploy code with SQL fast path behind `cel.enable_sql_metrics`.
2. Auto-create the new index in `_ensure_indexes()` on module update (metrics core).
3. Stage validation: run targeted tests; run an EXPLAIN on the INSELECT query to confirm index scans and
   partition pruning.
4. Enable in production; monitor query times and misses.

Monitoring/logging (minimal)

- Log per-execution path and status at INFO under `odoo.addons.spp_cel_domain`.
- Optional Prometheus hooks later; not required for V2.

---

## Acceptance Criteria

- SQL fast path returns the same IDs as the previous Python path for supported comparisons.
- Preview never calls providers; evaluate queues or refreshes as specified.
- No result truncation; no silent stale returns when previewing.
- Record rules remain enforced (no direct SQL leaks).
- New index is created automatically; no partial index on `NOW()` is introduced.

---

## Developer Notes & Edge Cases

- Type handling: Only run numeric casts when `jsonb_typeof(value_json)='number'` or value is clearly numeric.
  String comparisons use `::text` equality/inequality only in V2.
- Errors/missing: Exclude `error_code` rows; treat `NULL` as non-match.
- Multi-company: Always filter by `company_id` in the subquery; outer `search()` further enforces company
  rules.
- Params: Keep `params_hash` in all lookups; CEL V2 defaults to empty string unless translator provides
  params.
- Provider: Prefer registry `provider` label to match cached rows; default to metric name.
- Thresholds: Use `async_threshold` to decide between synchronous refresh and queueing in evaluate mode.

---

## Appendix A — Example SQL and Domains

Domain (numeric `>= 85`):

```
[('id', 'inselect', ("""
SELECT DISTINCT fv.subject_id
FROM openspp_feature_value fv
WHERE fv.company_id = %(company_id)s
  AND fv.metric = %(metric)s
  AND fv.subject_model = %(subject_model)s
  AND fv.period_key = %(period_key)s
  AND fv.provider = %(provider)s
  AND fv.params_hash = %(params_hash)s
  AND fv.error_code IS NULL
  AND (fv.expires_at IS NULL OR fv.expires_at > NOW())
  AND jsonb_typeof(fv.value_json) = 'number'
  AND (fv.value_json::numeric) >= %(rhs)s
""", {
  'company_id': 1,
  'metric': 'education.attendance_pct',
  'subject_model': 'res.partner',
  'period_key': '2024-09',
  'provider': 'education.attendance_pct',
  'params_hash': '',
  'rhs': 85,
}))]
```

---

## Appendix B — Task Checklist (copy/paste)

- [ ] Add index in `openspp_metrics._ensure_indexes()`.
- [ ] Add helpers in `cel.executor`: `_metric_registry_info`, `_metric_cache_status_sql`,
      `_metric_inselect_sql`.
- [ ] Update `_exec_metric` with preview gating, preflight, SQL fast path, and evaluate async/refresh logic.
- [ ] Enrich `metrics_info` with path/status for Explain.
- [ ] Add unit tests: numeric, string, preflight status.
- [ ] Add integration tests: preview gating, evaluate small/large cohorts.
- [ ] Verify record rules by a restricted user in a test.

---

End of V2
