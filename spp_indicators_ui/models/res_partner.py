from odoo import fields, models
from odoo.tools.safe_eval import safe_eval


class ResPartner(models.Model):
    _inherit = "res.partner"

    metrics_count = fields.Integer(compute="_compute_metrics_count", string="Metrics")

    def _compute_metrics_count(self):
        Feature = self.env["openspp.indicator.value"].sudo()
        # Scope by company for safety; subject_model is always res.partner here
        company_id = self.env.company.id
        for partner in self:
            partner.metrics_count = Feature.search_count(
                [
                    ("company_id", "=", company_id),
                    ("subject_model", "=", "res.partner"),
                    ("subject_id", "=", partner.id),
                ]
            )

    def action_open_metrics(self):
        self.ensure_one()
        action = self.env.ref("spp_indicators_ui.action_openspp_partner_metrics").read()[0]
        # Filter to this partner
        action["domain"] = [
            ("company_id", "=", self.env.company.id),
            ("subject_model", "=", "res.partner"),
            ("subject_id", "=", self.id),
        ]
        # Provide sensible defaults if user creates a row from the list (admins only)
        raw_ctx = action.get("context")
        if isinstance(raw_ctx, str):
            try:
                ctx = safe_eval(raw_ctx)
            except Exception:
                ctx = {}
        else:
            ctx = dict(raw_ctx or {})
        ctx.update(
            {
                "default_company_id": self.env.company.id,
                "default_subject_model": "res.partner",
                "default_subject_id": self.id,
            }
        )
        action["context"] = ctx
        return action
