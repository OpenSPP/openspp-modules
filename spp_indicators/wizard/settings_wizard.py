from __future__ import annotations

from odoo import api, fields, models


class OpensppIndicatorSettings(models.TransientModel):
    _name = "openspp.indicator.settings.wizard"
    _description = "Indicator Settings"

    allow_any_provider_fallback = fields.Boolean(
        string="Allow provider-agnostic cache fallback",
        help="Read cached values even if provider label differs or registry is missing (recommended ON in dev).",
    )

    @api.model
    def default_get(self, fields_list):
        vals = super().default_get(fields_list)
        ICP = self.env["ir.config_parameter"].sudo()
        vals["allow_any_provider_fallback"] = bool(
            int(ICP.get_param("openspp_metrics.allow_any_provider_fallback", "1"))
        )
        return vals

    def action_save(self):
        self.ensure_one()
        ICP = self.env["ir.config_parameter"].sudo()
        ICP.set_param("openspp_metrics.allow_any_provider_fallback", "1" if self.allow_any_provider_fallback else "0")
        return {"type": "ir.actions.act_window_close"}
