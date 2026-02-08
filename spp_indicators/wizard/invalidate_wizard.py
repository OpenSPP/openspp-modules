from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class OpensppIndicatorInvalidateWizard(models.TransientModel):
    _name = "openspp.indicator.invalidate.wizard"
    _description = "Invalidate Cached Metrics"

    metric_id = fields.Many2one(
        "openspp.indicator.definition", string="Indicator Definition", domain=[("active", "=", True)]
    )
    metric = fields.Char(required=True)
    subject_model = fields.Selection(selection=[("res.partner", "Partner")], default="res.partner", required=True)
    subject_model_code = fields.Char(default="res.partner", string="Subject Model (technical)")
    period_key = fields.Char()
    domain_text = fields.Char(string="Domain (on subject model)")
    recent_push_summary = fields.Text(string="Recent Activity", readonly=True)

    def action_run(self):
        self.ensure_one()
        model_name = self.metric_id.subject_model or self.subject_model_code or self.subject_model
        Model = self.env[model_name]
        subject_ids = []
        if self.domain_text:
            try:
                dom = safe_eval(self.domain_text)
                if isinstance(dom, list):
                    subject_ids = Model.search(dom).ids
            except Exception:
                subject_ids = []
        self.env["openspp.indicator.value"].sudo().invalidate(
            self.metric, model_name, self.period_key or None, subject_ids or None
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {"title": "Invalidated", "message": "Marked cached rows as expired.", "type": "success"},
        }

    @api.onchange("metric_id")
    def _onchange_metric_id(self):
        if self.metric_id:
            self.metric = self.metric_id.name
            model_name = self.metric_id.subject_model or "res.partner"
            self.subject_model_code = model_name
            selection_values = dict(self._fields["subject_model"].selection)
            if model_name in selection_values:
                self.subject_model = model_name
            self.recent_push_summary = self._build_push_summary(self.metric_id.name)
        else:
            self.recent_push_summary = False

    def _build_push_summary(self, metric_name: str) -> str:
        error_model = self.env["openspp.indicator.push.error"].sudo()
        unresolved = error_model.search_count([("metric", "=", metric_name), ("resolved", "=", False)])
        last_error = error_model.search([("metric", "=", metric_name)], order="create_date desc", limit=1)
        parts = [f"Unresolved errors: {unresolved}"]
        if last_error:
            parts.append(f"Last error on {fields.Datetime.to_string(last_error.create_date)} ({last_error.error_code})")
        return "\n".join(parts)
