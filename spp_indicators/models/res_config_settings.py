from __future__ import annotations

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    openspp_metrics_allow_any_provider_fallback = fields.Boolean(
        string="Allow provider-agnostic cache fallback",
        config_parameter="openspp_metrics.allow_any_provider_fallback",
        help=(
            "If enabled, evaluate() may read cached values even when the runtime provider registry "
            "is missing or provider labels differ. Recommended ON in development; consider OFF in "
            "production for stricter behavior."
        ),
        default=True,
    )

    # Existing settings referenced by settings_views.xml
    openspp_metrics_education_base_url = fields.Char(
        string="Education Base URL",
        config_parameter="openspp_metrics.education.base_url",
    )
    openspp_metrics_default_ttl = fields.Integer(
        string="Default TTL (seconds)",
        config_parameter="openspp_metrics.default_ttl",
        default=86400,
        help="Default cache TTL for providers that do not specify one.",
    )
    openspp_metrics_require_api_key = fields.Boolean(
        string="Require API Key for Metrics API",
        config_parameter="openspp_metrics.require_api_key",
        default=True,
    )
