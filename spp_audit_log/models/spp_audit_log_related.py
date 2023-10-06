import json

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SppAuditLogRelated(models.Model):
    _name = "spp.audit.log.related"

    name = fields.Char(compute="_compute_name")

    spp_audit_log_id = fields.Many2one("spp.audit.log", required=True)
    model_id = fields.Many2one(
        "ir.model",
        "Model",
        required=True,
        ondelete="cascade",
    )
    field_id = fields.Many2one(
        "ir.model.fields",
        required=True,
        ondelete="cascade",
    )
    field_id_domain = fields.Char(
        compute="_compute_field_id_domain",
        readonly=True,
    )

    @api.depends("spp_audit_log_id.name")
    def _compute_name(self):
        for rec in self:
            rec.name = f"{rec.spp_audit_log_id.name}: {rec.model_id.name} - {rec.field_id.name}"

    @api.constrains("field_id")
    def _check_field_id(self):
        for rec in self:
            if rec.field_id.relation != rec.spp_audit_log_id.model_id.model:
                msg = f"field's comodel should be {rec.spp_audit_log_id.model_id.name}"
                raise ValidationError(_(msg))

    @api.constrains("model_id")
    def _check_model_id(self):
        for rec in self:
            if rec.model_id == rec.spp_audit_log_id.model_id:
                raise ValidationError(
                    _("Related model should not be the same with the parent model.")
                )

    @api.depends("model_id")
    def _compute_field_id_domain(self):
        for rec in self:
            domain = [("id", "=", 0)]
            if rec.model_id:
                domain = [
                    ("model_id", "=", rec.model_id.id),
                    ("relation", "=", rec.spp_audit_log_id.model_id.model),
                ]
            rec.field_id_domain = json.dumps(domain)
