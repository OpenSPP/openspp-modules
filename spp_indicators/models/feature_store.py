from __future__ import annotations

import json
import logging
from typing import Any

from psycopg2.extras import execute_values

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class OpensppIndicatorValue(models.Model):
    _name = "openspp.indicator.value"
    _description = "OpenSPP Indicator Store Value"
    _rec_name = "metric"
    _table = "openspp_indicator_value"
    _log_access = False
    _order = "id DESC"

    metric = fields.Char(required=True, index=True)
    provider = fields.Char(index=True, default="")
    subject_model = fields.Char(required=True, index=True, default="res.partner")
    subject_id = fields.Integer(required=True, index=True)
    period_key = fields.Char(required=True, index=True)
    value_json = fields.Json()
    value_type = fields.Selection([("number", "Number"), ("string", "String"), ("json", "JSON")], default="json")
    params_hash = fields.Char(index=True, default="")
    coverage = fields.Float()
    as_of = fields.Datetime()
    fetched_at = fields.Datetime()
    expires_at = fields.Datetime()
    source = fields.Char()
    error_code = fields.Char()
    error_message = fields.Char()
    updated_at = fields.Datetime(default=fields.Datetime.now)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company.id, required=True, index=True)

    _sql_constraints = [
        (
            "uniq_metric_subject_period_params",
            "unique(metric,provider,subject_model,subject_id,period_key,params_hash,company_id)",
            "Metric value must be unique per subject/period/provider/params/company",
        ),
    ]

    def read(self, fields=None, load="_classic_read"):
        records = super().read(fields=fields, load=load)
        # Backward compatibility: expose provider="push" when rows were inserted
        # via the push API but stored with an empty provider label.
        if not fields or "provider" in fields:
            for vals in records:
                if (vals.get("provider") in (None, "")) and vals.get("source") == "push":
                    vals["provider"] = "push"
        return records

    @api.model
    def _ensure_base_table(self):
        """Create the feature store table if it is missing.

        Partitioning was originally planned but is disabled because PostgreSQL
        requires the primary key to include the partition key, while Odoo
        models rely on a single-column ``id`` primary key.
        """
        cr = self.env.cr
        # Detect existing table and whether it's partitioned
        cr.execute("SELECT to_regclass('public.openspp_indicator_value') IS NOT NULL")
        exists = cr.fetchone()[0]
        if not exists:
            # Create as standard heap table; partitioning is disabled in 17.4 because
            # PostgreSQL requires the primary key to include the partition key, but
            # Odoo models depend on a single-column `id` primary key.
            cr.execute(
                """
                CREATE TABLE openspp_indicator_value (
                    id serial PRIMARY KEY,
                    metric varchar NOT NULL,
                    provider varchar NOT NULL DEFAULT '',
                    subject_model varchar NOT NULL,
                    subject_id integer NOT NULL,
                    period_key varchar NOT NULL,
                    value_json jsonb,
                    value_type varchar,
                    params_hash varchar NOT NULL DEFAULT '',
                    coverage double precision,
                    as_of timestamp,
                    fetched_at timestamp,
                    expires_at timestamp,
                    source varchar,
                    error_code varchar,
                    error_message varchar,
                    updated_at timestamp default now(),
                    company_id integer NOT NULL,
                    UNIQUE(metric, provider, subject_model, subject_id, period_key, params_hash, company_id)
                );
                CREATE INDEX IF NOT EXISTS idx_ofv_metric_subject_period ON openspp_indicator_value (
                    company_id, metric, provider, subject_model, subject_id, period_key, params_hash
                );
                CREATE INDEX IF NOT EXISTS idx_ofv_metric_period ON openspp_indicator_value (
                    company_id, metric, period_key
                );
                CREATE INDEX IF NOT EXISTS idx_ofv_provider ON openspp_indicator_value (
                    company_id, provider
                );
                """
            )
        else:
            # Table exists — ensure indexes
            self._ensure_indexes()

    @api.model
    def _ensure_partitions(self, modulus: int = 16):
        # Partitioning disabled; no-op placeholder for forward compatibility.
        return

    @api.model
    def _ensure_indexes(self):
        cr = self.env.cr
        # Create critical indexes if missing
        cr.execute(
            "CREATE INDEX IF NOT EXISTS idx_ofv_metric_subject_period ON openspp_indicator_value ("
            "company_id, metric, provider, subject_model, subject_id, period_key, params_hash)"
        )
        cr.execute(
            "CREATE INDEX IF NOT EXISTS idx_ofv_metric_period ON openspp_indicator_value ("
            "company_id, metric, period_key)"
        )
        cr.execute("CREATE INDEX IF NOT EXISTS idx_ofv_provider ON openspp_indicator_value (company_id, provider)")
        # Subject-first composite index to accelerate INSELECT lookups from the subject side
        cr.execute(
            "CREATE INDEX IF NOT EXISTS idx_ofv_subject_company_metric_period ON openspp_indicator_value ("
            "subject_id, company_id, metric, subject_model, period_key, provider, params_hash)"
        )

    # Upsert helpers
    @api.model
    def upsert_values(self, rows: list[dict[str, Any]]):
        """Upsert multiple rows.

        Each row must include metric, subject_model, subject_id, period_key, value_json,
        value_type, as_of, expires_at, source.
        """
        if not rows:
            return {"inserted": 0, "updated": 0}
        cr = self.env.cr
        # Build INSERT ... ON CONFLICT statement
        values = []
        for r in rows:
            company_id = int(r.get("company_id") or self.env.company.id)
            value_json = r.get("value_json")
            values.append(
                (
                    r.get("metric"),
                    r.get("provider", ""),
                    r.get("subject_model", "res.partner"),
                    int(r.get("subject_id")),
                    r.get("period_key"),
                    json.dumps(value_json),
                    r.get("value_type", "json"),
                    r.get("params_hash", ""),
                    r.get("coverage"),
                    r.get("as_of"),
                    r.get("fetched_at"),
                    r.get("expires_at"),
                    r.get("source"),
                    r.get("error_code"),
                    r.get("error_message"),
                    company_id,
                )
            )
        query = """
            INSERT INTO openspp_indicator_value (
                metric, provider, subject_model, subject_id, period_key, value_json, value_type,
                params_hash, coverage, as_of, fetched_at, expires_at, source, error_code, error_message, company_id
            )
            VALUES %s
            ON CONFLICT (metric, provider, subject_model, subject_id, period_key, params_hash, company_id)
            DO UPDATE SET value_json = EXCLUDED.value_json,
                          value_type = EXCLUDED.value_type,
                          params_hash = EXCLUDED.params_hash,
                          coverage = EXCLUDED.coverage,
                          as_of = EXCLUDED.as_of,
                          fetched_at = EXCLUDED.fetched_at,
                          expires_at = EXCLUDED.expires_at,
                          source = EXCLUDED.source,
                          error_code = EXCLUDED.error_code,
                          error_message = EXCLUDED.error_message,
                          updated_at = now()
            RETURNING (xmax = 0) AS inserted
        """
        execute_values(cr, query, values, page_size=1000)
        result_rows = cr.fetchall()
        inserted = sum(1 for (flag,) in result_rows if flag)
        updated = len(result_rows) - inserted
        return {"inserted": inserted, "updated": updated}

    @api.model
    def cron_purge_expired(self, batch_param: str | None = None):
        icp = self.env["ir.config_parameter"].sudo()
        limit_param = batch_param or icp.get_param("openspp_metrics.expired_purge_batch", "5000")
        try:
            batch_size = max(int(limit_param), 0)
        except ValueError:
            batch_size = 5000
        if not batch_size:
            return 0
        cr = self.env.cr
        cr.execute(
            """
            WITH cte AS (
                SELECT id FROM openspp_indicator_value
                WHERE expires_at IS NOT NULL AND expires_at < NOW()
                LIMIT %s
            )
            DELETE FROM openspp_indicator_value WHERE id IN (SELECT id FROM cte)
            RETURNING id
            """,
            (batch_size,),
        )
        deleted = cr.rowcount or 0
        return deleted

    @api.model
    def read_values(
        self,
        metric: str,
        subject_model: str,
        subject_ids: list[int],
        period_key: str,
        *,
        provider: str = "",
        params_hash: str | None = "",
        company_id: int | None = None,
    ) -> dict[int, dict[str, Any]]:
        if not subject_ids:
            return {}
        q = self.env.cr
        if company_id is None:
            company_id = self.env.company.id
        params_filter = " AND params_hash = %s"
        args: list[Any] = [company_id, metric, provider or "", subject_model, period_key]
        if params_hash is None:
            params_filter = ""
        else:
            args.append(params_hash or "")
        args.append(subject_ids)
        q.execute(
            f"""
            SELECT subject_id, value_json, value_type, coverage, as_of, fetched_at, expires_at,
                   error_code, error_message
            FROM openspp_indicator_value
            WHERE company_id = %s AND metric = %s AND provider = %s AND subject_model = %s
              AND period_key = %s{params_filter} AND subject_id = ANY(%s)
            """,
            tuple(args),
        )
        res = {}
        for sid, vj, vt, cov, as_of, fetched_at, expires_at, ec, em in q.fetchall():
            res[sid] = {
                "value": vj,
                "type": vt,
                "coverage": cov,
                "as_of": as_of,
                "fetched_at": fetched_at,
                "expires_at": expires_at,
                "error_code": ec,
                "error_message": em,
            }
        return res

    @api.model
    def read_values_any_provider(
        self,
        metric: str,
        subject_model: str,
        subject_ids: list[int],
        period_key: str,
        *,
        params_hash: str | None = "",
        company_id: int | None = None,
    ) -> dict[int, dict[str, Any]]:
        """Read cached values ignoring provider filter (best-effort fallback).

        Useful when the runtime registry is not yet populated but cached rows
        exist from a previous run under a specific provider label.
        """
        if not subject_ids:
            return {}
        q = self.env.cr
        if company_id is None:
            company_id = self.env.company.id
        params_filter = " AND params_hash = %s"
        args: list[Any] = [company_id, metric, subject_model, period_key]
        if params_hash is None:
            params_filter = ""
        else:
            args.append(params_hash or "")
        args.append(subject_ids)
        q.execute(
            f"""
            SELECT subject_id, value_json, value_type, coverage, as_of, fetched_at, expires_at,
                   error_code, error_message
            FROM openspp_indicator_value
            WHERE company_id = %s AND metric = %s AND subject_model = %s AND period_key = %s
              {params_filter} AND subject_id = ANY(%s)
            """,
            tuple(args),
        )
        res: dict[int, dict[str, Any]] = {}
        for sid, vj, vt, cov, as_of, fetched_at, expires_at, ec, em in q.fetchall():
            res[sid] = {
                "value": vj,
                "type": vt,
                "coverage": cov,
                "as_of": as_of,
                "fetched_at": fetched_at,
                "expires_at": expires_at,
                "error_code": ec,
                "error_message": em,
            }
        return res

    @api.model
    def invalidate(
        self,
        metric: str,
        subject_model: str,
        period_key: str | None = None,
        subject_ids: list[int] | None = None,
        *,
        provider: str = "",
        params_hash: str = "",
        company_id: int | None = None,
    ):
        """Mark cached values as expired matching the filters provided."""
        cr = self.env.cr
        if company_id is None:
            company_id = self.env.company.id
        if subject_ids and period_key:
            cr.execute(
                """
                UPDATE openspp_indicator_value SET expires_at = NOW()
                WHERE company_id = %s AND metric = %s AND provider = %s AND subject_model = %s
                  AND period_key = %s AND params_hash = %s AND subject_id = ANY(%s)
                """,
                (company_id, metric, provider or "", subject_model, period_key, params_hash or "", subject_ids),
            )
        elif period_key:
            cr.execute(
                """
                UPDATE openspp_indicator_value SET expires_at = NOW()
                WHERE company_id = %s AND metric = %s AND provider = %s AND subject_model = %s
                  AND period_key = %s AND params_hash = %s
                """,
                (company_id, metric, provider or "", subject_model, period_key, params_hash or ""),
            )
        else:
            cr.execute(
                """
                UPDATE openspp_indicator_value SET expires_at = NOW()
                WHERE company_id = %s AND metric = %s AND provider = %s AND subject_model = %s AND params_hash = %s
                """,
                (company_id, metric, provider or "", subject_model, params_hash or ""),
            )
