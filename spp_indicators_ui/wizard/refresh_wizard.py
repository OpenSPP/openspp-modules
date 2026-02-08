from __future__ import annotations

from odoo import fields, models


class OpensppIndicatorRefreshWizard(models.TransientModel):
    _name = "openspp.indicator.refresh.wizard"
    _description = "Refresh Indicators for Partner"

    partner_id = fields.Many2one("res.partner", required=True)
    metric = fields.Char(required=True, help="Qualified metric name, e.g., household.size")
    period_key = fields.Char(required=True, default="current")

    def action_refresh(self):
        self.ensure_one()
        svc = self.env["openspp.indicator"]
        # Force refresh of this metric for this partner
        svc.evaluate(self.metric, "res.partner", [self.partner_id.id], self.period_key, mode="refresh")
        # Open metrics list
        return self.partner_id.action_open_metrics()
