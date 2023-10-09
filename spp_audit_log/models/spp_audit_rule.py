from odoo import api, fields, models

from ..tools import audit_decorator


class SppAuditLog(models.Model):
    _name = "spp.audit.rule"
    _description = "SPP Audit Log"

    name = fields.Char(size=32, required=True)
    # active = fields.Boolean(default=True)
    log_create = fields.Boolean("Log Creation", default=True)
    log_write = fields.Boolean("Log Update", default=True)
    log_unlink = fields.Boolean("Log Deletion", default=True)
    model_id = fields.Many2one(
        "ir.model",
        "Model",
        required=True,
        domain=[("is_mail_thread", "=", True)],
        ondelete="cascade",
    )
    related_model_ids = fields.One2many("spp.audit.rule.related", "spp_audit_rule_id")

    _sql_constraints = [
        (
            "model_uniq",
            "unique(model_id)",
            "There is already a rule defined on this model",
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
    def get_audit_rule(self, method):
        domain = [("model_id.model", "=", self._name)]
        if method == "create":
            domain.append(("log_create", "=", True))
        elif method == "write":
            domain.append(("log_write", "=", True))
        elif method == "unlink":
            domain.append(("log_unlink", "=", True))

        return self.env["spp.audit.rule"].search(domain, limit=1)

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

            # Add attribute get_audit_rule to models that are being created or updated in spp.audit.rule
            type(RecordModel).get_audit_rule = SppAuditLog.get_audit_rule

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

    def log(self, method, old_values=None, new_values=None):
        self.ensure_one()
        if old_values or new_values:
            data = self._format_data_to_log(old_values, new_values)
            self.send_log_message(method, data)
        return

    def send_log_message(self, method, data):
        self.ensure_one()
        for res_id in data:
            record_model = self.env[self.sudo().model_id.model]
            record = record_model.browse(res_id)
            related_model_records = []
            for related_model in self.related_model_ids:
                related_model_records.append(
                    self.env[related_model.model_id.model].search(
                        [(related_model.field_id.name, "=", res_id)]
                    )
                )

            if method == "create":
                msg = f"{data[res_id]['new'].get('name')} is Created."
                record.message_post(body=msg)
                for related_model_record in related_model_records:
                    for model_record in related_model_record:
                        model_record.message_post(body=msg)
            elif method == "write":
                old_data = data[res_id]["old"]
                new_data = data[res_id]["new"]

                for old_data_field_name, new_data_field_name in zip(old_data, new_data):
                    field = record._fields.get(new_data_field_name)
                    field_label = field.get_description(self.env)["string"]
                    msg = (
                        f"{field_label} is updated from {old_data[old_data_field_name]} "
                        f"to {new_data[new_data_field_name]}"
                    )
                    record.message_post(body=msg)

                    updated_msg = f"{self.model_id.name} ({record.name}): {msg}"
                    for related_model_record in related_model_records:
                        for model_record in related_model_record:
                            model_record.message_post(body=updated_msg)
            elif method == "unlink":
                # TODO: add message_post for deleting records
                pass
        return
