from __future__ import annotations

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class OpensppIndicatorDefinition(models.Model):
    _name = "openspp.indicator.definition"
    _description = "OpenSPP Metric Definition"
    _order = "name"

    PERIOD_GRANULARITY = [
        ("day", "Day"),
        ("week", "Week"),
        ("month", "Month"),
        ("quarter", "Quarter"),
        ("year", "Year"),
        ("cycle", "Program Cycle"),
        ("rolling", "Rolling Window"),
        ("snapshot", "Snapshot Date"),
        ("custom", "Custom"),
        ("static", "Always Valid"),
    ]

    name = fields.Char(required=True, index=True)
    subject_model = fields.Char(
        required=True, default="res.partner", help="Odoo model name representing the subject, e.g. res.partner."
    )
    description = fields.Text()
    value_type = fields.Selection(
        [("number", "Number"), ("string", "String"), ("json", "JSON")], required=True, default="number"
    )
    period_granularity = fields.Selection(PERIOD_GRANULARITY, required=True, default="month")
    params_schema = fields.Json(help="Optional JSON schema describing expected params payload.")
    owner_group = fields.Many2one(
        "res.groups", string="Owner Group", help="Owning team responsible for this metric definition."
    )
    default_ttl_seconds = fields.Integer(default=0, help="Default TTL (seconds) applied when pushes omit expires_at.")
    id_mapping_fields = fields.Char(
        help="Comma-separated fallback chain of fields used to resolve external identifiers."
    )
    id_mapping_required = fields.Boolean(default=False, help="If enabled, rows without matching subjects are rejected.")
    id_mapping_namespace = fields.Char(
        help="Optional namespace key describing which external identifier system is expected."
    )
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True, index=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "openspp_metrics_definition_name_uniq",
            "unique(name, company_id)",
            "Metric names must be unique per company.",
        ),
    ]

    @api.constrains("name")
    def _check_name_format(self):
        import re

        regex = re.compile(r"^[a-z0-9]+(\.[a-z0-9_]+)+$")
        for rec in self:
            if not regex.match(rec.name):
                raise ValidationError("Metric name must use dotted lowercase namespaces, e.g. program.metric_name.")

    @api.constrains("default_ttl_seconds")
    def _check_default_ttl(self):
        for rec in self:
            if rec.default_ttl_seconds and rec.default_ttl_seconds < 0:
                raise ValidationError("Default TTL must be zero or positive.")

    @api.model
    def normalize_mapping_fields(self, fields_value: str) -> list[str]:
        if not fields_value:
            return []
        return [f.strip() for f in fields_value.split(",") if f.strip()]

    def get_mapping_fields(self) -> list[str]:
        self.ensure_one()
        return self.normalize_mapping_fields(self.id_mapping_fields)

    def matches_pattern(self, metric_name: str) -> bool:
        self.ensure_one()
        return self.name == metric_name

    def get_mapping_config(self) -> dict:
        self.ensure_one()
        return {
            "fields": self.get_mapping_fields(),
            "required": bool(self.id_mapping_required),
            "namespace": (self.id_mapping_namespace or "").strip(),
        }
