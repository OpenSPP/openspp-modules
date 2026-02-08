from __future__ import annotations

from odoo import api, fields, models


class OpensppIndicatorProvider(models.Model):
    _name = "openspp.indicator.provider"
    _description = "OpenSPP Metrics Provider Configuration"

    name = fields.Char(required=True)
    metric = fields.Char(required=True, help="Qualified metric name e.g. education.attendance_pct")
    base_url = fields.Char()
    auth_type = fields.Selection(
        [("none", "None"), ("api_key", "API Key"), ("oauth2", "OAuth2"), ("hmac", "HMAC")], default="none"
    )
    api_key = fields.Char()
    default_ttl = fields.Integer(default=86400)
    max_batch_size = fields.Integer(default=5000)
    recommended_concurrency = fields.Integer(default=4)
    timeout_ms = fields.Integer(default=5000)
    retry_max = fields.Integer(default=0)
    id_mapping_fields = fields.Char(help="Comma-separated field chain e.g. school_student_id,external_id,national_id")
    id_mapping_required = fields.Boolean(default=False)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    _sql_constraints = [
        (
            "openspp_provider_name_metric_company_unique",
            "unique(name, metric, company_id)",
            "A provider with the same name and metric already exists for this company.",
        )
    ]

    @api.model
    def to_registry_info(self, rec):
        id_fields = []
        if rec.id_mapping_fields:
            id_fields = [s.strip() for s in rec.id_mapping_fields.split(",") if s.strip()]
        return {
            "id_mapping": {"fields": id_fields, "required": rec.id_mapping_required},
            "capabilities": {
                "supports_batch": True,
                "max_batch_size": rec.max_batch_size,
                "default_ttl": rec.default_ttl,
                "recommended_concurrency": rec.recommended_concurrency,
            },
        }
