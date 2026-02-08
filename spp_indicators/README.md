# OpenSPP Metrics Core (Odoo 17)

Cross-cutting subsystem for computing and serving external/internal metrics used across OpenSPP, including CEL
filters.

## What it provides

- Metric definition registry: `openspp.metrics.definition` (names, types, periods, TTL, ID mapping).
- In-memory provider registry: `openspp.indicator.registry` (Python-backed store).
- Feature store model: `openspp.indicator.value` (table `openspp_feature_value`).
- Service: `openspp.metrics.evaluate(metric, subject_model, subject_ids, period_key, mode)`.
- HTTP endpoints:
  - `POST /api/indicators/push` — push indicator values (auth: `X-Api-Key` or admin session).
  - `POST /api/indicators/invalidate` — expire cached values.
- API credential model: `openspp.metrics.api_credential` (per-integration tokens, rate limits).
- Push error log: `openspp.metrics.push.error` for monitoring inbound failures.
- Built-in provider example: `household.size` (active member count by group).
- Admin tooling: metric definitions, feature store inspector, dashboard (graph/pivot), push error monitor,
  queue wizards.

## Usage from CEL

Install together with `cel_domain`. Then analysts can write:

```cel
metric("household.size", me, "current") >= 2
metric("education.attendance_pct", me, "2024-09") >= 85
```

Aggregators (when used from Groups profile)

```cel
avg_over(members, metric("education.attendance_pct", m, "2024-09")) >= 80
coverage_over(members, metric("education.attendance_pct", m, "2024-09")) >= 0.8
all_over(members, metric("education.attendance_pct", m, "2024-09") >= 85)
```

Cycle helpers (via CEL): `last_cycle(program("Program Name"))`, `first_cycle(...)`, `previous(cycle_key)`,
`next(cycle_key)`.

## Provider registration

Two options (both supported):

- Static (recommended for deterministic startup/tests):

```python
from odoo.addons.spp_indicators.models.metric_registry import register_static
register_static(
    name='education.attendance_pct',
    handler=MyAttendanceProvider(),
    return_type='number',
    subject_model='res.partner',
    capabilities={'supports_batch': True, 'default_ttl': 86400},
)
```

- Dynamic (via Odoo model):

```python
self.env['openspp.indicator.registry'].register(
    name='education.attendance_pct', handler=MyAttendanceProvider(), return_type='number'
)
```

Providers implement `compute_batch(env, ctx, subject_ids) -> dict[subject_id, value]`.

Provider configuration (runtime overrides)

- Model: `openspp.metrics.provider` under Settings > Metrics > Providers
- Fields:
  - `id_mapping_fields` (comma-separated), `id_mapping_required`
  - `default_ttl`, `max_batch_size`, `recommended_concurrency` These settings override registry defaults
    during evaluation.

## Configuration checklist

1. Create a Metric Definition (Metrics ▸ Definitions) with canonical name, value type, period granularity,
   TTL, and optional ID-mapping rules.
2. Issue an API credential (Metrics ▸ API Credentials). Distribute the plain token to OpenFn or other
   integrators.
3. Optional: configure provider overrides if the metric is also computed dynamically.
4. Monitor pushes through the Dashboard and Push Errors menus.

## Push API

Example payload:

```json
{
  "metric": "health.vaccination",
  "period_key": "2025-09",
  "params": {"program": "EPI"},
  "subject_external_id_type": "dhis2_tei",
  "items": [{"subject_external_id": "TEI123", "value": 1, "as_of": "2025-09-12T12:30:00Z"}],
  "source_ref": "openfn.job.42"
}
```

- Supply the token issued in Metrics ▸ API Credentials via the `X-Api-Key` header.
- When `subject_id` is omitted, the push endpoint resolves `subject_external_id` using the mapping configured
  on the metric definition or provider.
- If `expires_at` is not provided, the system falls back to the definition/provider TTL.
- Include `errors_only: true` to dry-run validation without writing to the feature store.

## Notes

- Feature values are retained until `expires_at` or purged by the scheduled cleanup jobs; adjust retention
  with `openspp_metrics.expired_purge_batch`.
- Push errors are retained for 90 days by default (`openspp_metrics.push_error_retention_days`).
- Row access rules are not defined (read-only by administrators); adjust per deployment if end-users need to
  see metric materializations.
