# OpenSPP Metrics UI for Registrants

Adds a smart button "Metrics" on res.partner (used for both Individuals and Groups in OpenG2P/OpenSPP) that
opens a list of cached metric values from `openspp.indicator.value` for the current record.

- Depends on: `openspp_metrics`
- Works for both individuals and groups (same `res.partner` model; differentiated by `is_group`).

## What it shows

- Metric name, provider, period key
- Value JSON (in form), value type, coverage
- Timestamps (as_of, fetched_at, expires_at) and any error info

## How to use

1. Ensure `openspp_metrics` is installed and metric values exist in the feature store (via push API or
   provider evaluation).
2. Open an Individual or Group (res.partner) record.
3. Click the "Metrics" smart button to see values related to that record.

No additional menus are added; the UI is attached directly to partner forms.
