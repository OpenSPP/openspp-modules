from __future__ import annotations

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class OpensppIndicatorPushError(models.Model):
    _name = "openspp.indicator.push.error"
    _description = "OpenSPP Metrics Push Error"
    _order = "create_date desc"

    metric = fields.Char(required=True, index=True)
    subject_reference = fields.Char(help="External identifier or subject ID associated with the failure.")
    error_code = fields.Char(required=True, help="Stable error code to help integrations react.")
    error_message = fields.Text(required=True)
    payload = fields.Json(help="Original payload item (sanitized) to aid debugging.")
    credential_id = fields.Many2one("openspp.indicator.api_credential", index=True)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True, index=True)
    resolved = fields.Boolean(default=False)
    resolved_at = fields.Datetime(readonly=True)
    resolved_by = fields.Many2one("res.users", readonly=True)

    def action_mark_resolved(self):
        now = fields.Datetime.now()
        user = self.env.user
        for rec in self:
            rec.write({"resolved": True, "resolved_at": now, "resolved_by": user.id})
        return True

    @api.model
    def log_error(
        self, metric: str, error_code: str, message: str, *, credential=None, payload=None, subject_ref: str = ""
    ):
        vals = {
            "metric": metric,
            "error_code": error_code,
            "error_message": message,
            "subject_reference": subject_ref,
            "payload": payload or {},
            "resolved": False,
            "company_id": self.env.company.id,
        }
        if credential:
            vals["credential_id"] = credential.id
        return self.sudo().create(vals)

    @api.model
    def cron_purge_old(self):
        icp = self.env["ir.config_parameter"].sudo()
        retention = icp.get_param("openspp_metrics.push_error_retention_days", "90")
        try:
            retention_days = max(int(retention), 0)
        except ValueError:
            retention_days = 90
        if not retention_days:
            return 0
        cutoff_dt = fields.Datetime.to_datetime(fields.Datetime.now()) - relativedelta(days=retention_days)
        to_unlink = self.sudo().search([("create_date", "<", fields.Datetime.to_string(cutoff_dt))], limit=1000)
        count = len(to_unlink)
        if count:
            to_unlink.unlink()
        return count
