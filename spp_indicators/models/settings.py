from __future__ import annotations

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    openspp_metrics_education_base_url = fields.Char(string="Education Metrics Base URL")
    openspp_metrics_default_ttl = fields.Integer(string="Default TTL (seconds)", default=86400)
    openspp_metrics_require_api_key = fields.Boolean(string="Require API Key for Metrics API", default=True)

    def set_values(self):
        super().set_values()
        ICP = self.env["ir.config_parameter"].sudo()
        ICP.set_param("openspp_metrics.education.base_url", self.openspp_metrics_education_base_url or "")
        if self.openspp_metrics_default_ttl is not None:
            ICP.set_param("openspp_metrics.default_ttl", str(int(self.openspp_metrics_default_ttl)))
        ICP.set_param("openspp_metrics.require_api_key", "1" if self.openspp_metrics_require_api_key else "0")

    @api.model
    def get_values(self):
        res = super().get_values()
        ICP = self.env["ir.config_parameter"].sudo()
        res.update(
            openspp_metrics_education_base_url=ICP.get_param("openspp_metrics.education.base_url", default=""),
            openspp_metrics_default_ttl=int(ICP.get_param("openspp_metrics.default_ttl", default="86400") or 86400),
            openspp_metrics_require_api_key=(
                ICP.get_param("openspp_metrics.require_api_key", default="1") in ("1", "true", "True")
            ),
        )
        return res
