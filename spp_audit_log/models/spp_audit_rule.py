import json

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from ..tools import audit_decorator


class SppAuditRule(models.Model):
    _name = "spp.audit.rule"
    _description = "SPP Audit Rule"

    name = fields.Char(size=32, required=True)
    # TODO: should we need to add active field?
    # active = fields.Boolean(default=True)
    log_create = fields.Boolean("Log Creation", default=True)
    log_write = fields.Boolean("Log Update", default=True)
    log_unlink = fields.Boolean("Log Deletion", default=True)
    model_id = fields.Many2one(
        "ir.model",
        "Model",
        required=True,
        ondelete="cascade",
    )
    model_id_domain = fields.Char(
        compute="_compute_model_id_domain",
        readonly=True,
    )
    parent_id = fields.Many2one("spp.audit.rule", string="Parent Rule")
    child_ids = fields.One2many(
        "spp.audit.rule", "parent_id", string="Related Rules", readonly=True
    )

    # will be visible and used only if audit rule have parent
    field_id = fields.Many2one(
        "ir.model.fields",
        ondelete="cascade",
    )
    field_id_domain = fields.Char(
        compute="_compute_field_id_domain",
        readonly=True,
    )

    _sql_constraints = [
        (
            "model_uniq",
            "unique(model_id, parent_id)",
            "There is already a rule defined for this model and parent",
        ),
    ]

    _methods = ["create", "write", "_write", "unlink"]

    _ignored_fields = [
        "__last_update",
        "message_ids",
        "message_last_post",
        "write_date",
    ]

    @api.model
    def get_audit_rules(self, method):
        domain = [("model_id.model", "=", self._name)]
        if method == "create":
            domain.append(("log_create", "=", True))
        elif method == "write":
            domain.append(("log_write", "=", True))
        elif method == "unlink":
            domain.append(("log_unlink", "=", True))

        return self.env["spp.audit.rule"].search(domain)

    @api.model
    def _register_hook(self, ids=None):
        self = self.sudo()
        updated = False
        if ids:
            rules = self.browse(ids)
        else:
            rules = self.search([])
        for rule in rules:
            if rule.model_id.model not in self.env.registry.models:
                continue
            RecordModel = self.env[rule.model_id.model]

            # Add attribute get_audit_rules to models that are being created or updated in spp.audit.rule
            type(RecordModel).get_audit_rules = SppAuditRule.get_audit_rules

            for method in self._methods:
                func = getattr(RecordModel, method)
                while hasattr(func, "origin"):
                    if func.__name__.startswith("audit_"):
                        break
                    func = func.origin
                else:
                    RecordModel._patch_method(method, audit_decorator(method))
            updated = bool(ids)
        if updated:
            self.clear_caches()
        return updated

    @api.model
    @api.returns("self", lambda value: value.id)
    def create(self, vals):
        rule = super().create(vals)
        if self._register_hook(rule.id):
            self.pool.signal_changes()
        return rule

    def write(self, vals):
        res = super().write(vals)
        if self._register_hook(self._ids):
            self.pool.signal_changes()
        return res

    @classmethod
    def _format_data_to_log(cls, old_values, new_values):
        data = {}
        for age in ("old", "new"):
            vals_list = old_values if age == "old" else new_values
            if isinstance(vals_list, dict):
                vals_list = [vals_list]
            for vals in vals_list or []:
                for field in cls._ignored_fields:
                    vals.pop(field, None)
                res_id = vals.pop("id")
                if vals:
                    data.setdefault(res_id, {"old": {}, "new": {}})[age] = vals
        for res_id in list(data.keys()):
            all_fields = set(data[res_id]["old"].keys()) | set(
                data[res_id]["new"].keys()
            )
            for field in all_fields:
                if data[res_id]["old"].get(field) == data[res_id]["new"].get(field):
                    del data[res_id]["old"][field]
                    del data[res_id]["new"][field]
            if data[res_id]["old"] == data[res_id]["new"]:
                del data[res_id]
        return data

    @api.depends("model_id", "parent_id")
    def _compute_field_id_domain(self):
        for rec in self:
            domain = [("id", "=", 0)]
            if rec.model_id and rec.parent_id:
                domain = [
                    ("model_id", "=", rec.model_id.id),
                    ("relation", "=", rec.parent_id.model_id.model),
                ]
            rec.field_id_domain = json.dumps(domain)

    @api.depends("parent_id")
    def _compute_model_id_domain(self):
        for rec in self:
            # If rule doesn't have a parent rule, selection model should have inherit the mail.thread
            # Else, all model can be selected
            domain = [("is_mail_thread", "=", True)]
            if rec.parent_id:
                domain = []
            rec.model_id_domain = json.dumps(domain)

    @api.constrains("model_id")
    def _check_model_id(self):
        for rec in self:
            if not rec.parent_id and not rec.model_id.is_mail_thread:
                raise ValidationError(
                    _("Model should have inherit the mail.thread model.")
                )

    @api.constrains("field_id")
    def _check_field_id(self):
        for rec in self:
            if rec.parent_id and not rec.field_id:
                raise ValidationError(
                    _("Field is required if the rule is a child rule.")
                )

    @api.constrains("model_id", "field_id")
    def _check_model_id_field_id(self):
        for rec in self:
            if not rec.parent_id and not rec.model_id.is_mail_thread:
                raise ValidationError(
                    _(
                        "Model should have inherit the mail.thread model if rule is a parent rule."
                    )
                )
            if rec.parent_id and not rec.field_id:
                raise ValidationError(
                    _("Field is required if the rule is a child rule.")
                )
            if rec.parent_id and rec.field_id.relation != rec.parent_id.model_id.model:
                error_msg = f"Field's relation should be {rec.parent_id.model_id.name}"
                raise ValidationError(_(error_msg))

    def get_most_parent(self, res_ids):
        if not self.parent_id:
            return None, []

        # Initialize variable to be used in while loop
        current_rule_id = self
        parent_rule_id = self.parent_id
        currect_model_records = {"model": self.model_id.model, "ids": res_ids}

        # get the model name and ids of the most parent rule
        # loop will break if a rule doesn't have parent rule
        while parent_rule_id:
            current_records = self.env[currect_model_records["model"]].browse(
                currect_model_records["ids"]
            )
            currect_model_records["model"] = parent_rule_id.model_id.model
            new_ids = []
            for record in current_records:
                new_ids.extend(getattr(record, current_rule_id.field_id.name).ids)
            currect_model_records["ids"] = new_ids

            current_rule_id = parent_rule_id
            parent_rule_id = parent_rule_id.parent_id

        return currect_model_records["model"], [
            str(record_id) for record_id in currect_model_records["ids"]
        ]

    def log(self, method, old_values=None, new_values=None):
        self.ensure_one()
        if old_values or new_values:
            data = self._format_data_to_log(old_values, new_values)
            audit_log = self.env["spp.audit.log"].sudo()
            for res_id in data:
                parent_model, parent_res_ids = self.get_most_parent([res_id])
                audit_log.create(
                    {
                        # TODO: should we need to connect spp.audit.log to spp.audit.rule?
                        # 'audit_rule_id': self.id,
                        "user_id": self._uid,
                        "model_id": self.sudo().model_id.id,
                        "res_id": res_id,
                        "method": method,
                        "data": repr(data[res_id]),
                        "parent_model_id": self.env["ir.model"]
                        .search([("model", "=", parent_model)], limit=1)
                        .id,
                        "parent_res_ids_str": ",".join(parent_res_ids),
                    }
                )
        return
