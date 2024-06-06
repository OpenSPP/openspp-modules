import json

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from ..tools import audit_decorator


class SppAuditRule(models.Model):
    _name = "spp.audit.rule"
    _description = "SPP Audit Rule"

    name = fields.Char(required=True)
    # TODO: should we need to add active field?
    # active = fields.Boolean(default=True)
    log_create = fields.Boolean("Log Creation", default=True)
    log_write = fields.Boolean("Log Update", default=True)
    log_unlink = fields.Boolean("Log Deletion", default=True)
    view_logs = fields.Boolean("View Logs Action Menu", default=True)
    model_id = fields.Many2one(
        "ir.model",
        "Model",
        required=True,
        ondelete="cascade",
    )

    field_to_log_ids = fields.Many2many("ir.model.fields", string="Fields to log")
    field_to_log_ids_domain = fields.Char(
        compute="_compute_field_to_log_ids_domain",
        readonly=True,
    )

    action_id = fields.Many2one("ir.actions.act_window", "Add in the 'More' menu", readonly=True)

    _sql_constraints = [
        (
            "name_uniq",
            "unique(name)",
            "Name must be unique",
        ),
    ]

    _methods = ["create", "write", "_write", "unlink"]

    _ignored_fields = [
        "__last_update",
        "message_ids",
        "message_last_post",
        "write_date",
    ]

    @api.constrains("model_id")
    def _check_model(self):
        for rec in self:
            if self.env[self._name].search_count([("model_id", "=", rec.model_id.id), ("id", "!=", rec.id)]):
                raise ValidationError(_("A rule is already existed for the selected model."))

    def _process_action_id(self):
        for rec in self:
            if rec.view_logs:
                if not rec.action_id:
                    # Check action menu if view audit logs for a model is already existing
                    ir_act_window_id = self.env["ir.actions.act_window"].search(
                        [
                            ("binding_model_id", "=", rec.model_id.id),
                            ("res_model", "=", "spp.audit.log"),
                            ("name", "=", "View logs"),
                        ],
                        limit=1,
                    )

                    if ir_act_window_id:
                        # If action menu is existing, save existing action menu to action_id
                        ir_act_window_id.update(
                            {
                                "binding_view_types": "form",
                            }
                        )
                        rec.action_id = ir_act_window_id
                    else:
                        # Create action menu
                        vals = {
                            "name": _("View logs"),
                            "res_model": "spp.audit.log",
                            "binding_model_id": rec.model_id.id,
                            "binding_view_types": "form",
                            "domain": "[('model_id','=', {}), "
                            "('res_id', '=', active_id), ('method', 'in', {})]".format(
                                rec.model_id.id,
                                [method.replace("_", "") for method in self._methods],
                            ),
                        }
                        rec.action_id = self.env["ir.actions.act_window"].create(vals)
            else:
                action_menu = rec.action_id
                if action_menu:
                    action_menu.unlink()
        return

    @api.model
    def get_audit_rules(self, method):
        """
        The function returns audit rules based on the specified method.

        :param method: The "method" parameter is a string that specifies the type of operation being
        performed. It can have one of the following values: "create", "write", or "unlink"
        :return: The method is returning a search result of "spp.audit.rule" records based on the
        specified domain.
        """
        domain = [("model_id.model", "=", self._name)]
        if method == "create":
            domain.append(("log_create", "=", True))
        elif method == "write":
            domain.append(("log_write", "=", True))
        elif method == "unlink":
            domain.append(("log_unlink", "=", True))

        return self.env["spp.audit.rule"].sudo().search(domain)

    @api.model
    def _register_hook(self, ids=None):
        """
        The function `_register_hook` adds a decorator to certain methods of models in order to enable
        auditing.

        :param ids: The `ids` parameter is a list of record IDs. It is used to specify a subset of
        records on which the hook should be registered. If `ids` is not provided or is an empty list,
        the hook will be registered on all records of the model
        :return: a boolean value indicating whether any updates were made.
        """
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
                    # Monkey patch the methods to add a decorator
                    RecordModel._patch_method(method, audit_decorator(method))
            updated = bool(ids)
        if updated:
            self.env.registry.clear_cache()
        return updated

    @api.model
    @api.returns("self", lambda value: value.id)
    def create(self, vals):
        rule = super().create(vals)
        rule._process_action_id()
        if self._register_hook(rule.id):
            self.pool.signal_changes()
        return rule

    def write(self, vals):
        res = super().write(vals)
        self._process_action_id()
        if self._register_hook(self._ids):
            self.pool.signal_changes()
        return res

    def unlink(self):
        for rec in self:
            # get number of audit rule with the same model
            audit_rule_count = len(self.env["spp.audit.rule"].search([("model_id", "=", rec.model_id.id)]))

            # if only 1 and with menu action, unlink menu action
            if audit_rule_count == 1 and rec.action_id:
                rec.action_id.unlink()

            return super(SppAuditRule, rec).unlink()

    @classmethod
    def _format_data_to_log(cls, old_values, new_values, fields_to_log):
        """
        The function `_format_data_to_log` takes in old and new values, removes ignored fields, compares
        the values, and returns a dictionary of data with differences between old and new values.

        :param cls: The parameter `cls` refers to the class itself. It is used to access class
        attributes and methods within the method
        :param old_values: The parameter "old_values" is a list of dictionaries representing the old
        values of some data. Each dictionary represents a set of values for a specific data record
        :param new_values: The `new_values` parameter is a list of dictionaries or a single dictionary
        containing the new values for a particular resource. Each dictionary represents a resource and
        its corresponding field-value pairs
        :return: a dictionary containing the formatted data. The dictionary has resource IDs as keys,
        and the values are dictionaries with "old" and "new" keys. The "old" and "new" dictionaries
        contain the field-value pairs for the old and new values respectively.
        """
        data = {}
        for age in ("old", "new"):
            vals_list = old_values if age == "old" else new_values
            if isinstance(vals_list, dict):
                vals_list = [vals_list]
            for vals in vals_list or []:
                res_id = vals.pop("id")
                vals = dict(filter(lambda x: x[0] in fields_to_log, vals.items()))
                if vals:
                    data.setdefault(res_id, {"old": {}, "new": {}})[age] = vals
        for res_id in list(data.keys()):
            all_fields = set(data[res_id]["old"].keys()) | set(data[res_id]["new"].keys())
            for field in all_fields:
                if data[res_id]["old"].get(field) == data[res_id]["new"].get(field):
                    del data[res_id]["old"][field]
                    del data[res_id]["new"][field]
            if data[res_id]["old"] == data[res_id]["new"]:
                del data[res_id]
        return data

    @api.depends("model_id")
    def _compute_field_to_log_ids_domain(self):
        for rec in self:
            domain = [("id", "=", 0)]
            if rec.model_id:
                domain = [
                    ("model_id", "=", rec.model_id.id),
                    ("name", "not in", self._ignored_fields),
                ]
            rec.field_to_log_ids_domain = json.dumps(domain)

    @api.onchange("model_id")
    def _onchange_model_id(self):
        if self.model_id:
            self.update(
                {
                    "field_to_log_ids": None,
                }
            )

        return

    def get_audit_log_vals(self, res_id, method, data):
        self.ensure_one()
        return {
            # TODO: should we need to connect spp.audit.log to spp.audit.rule?
            # 'audit_rule_id': self.id,
            "user_id": self._uid,
            "model_id": self.sudo().model_id.id,
            "res_id": res_id,
            "method": method,
            "data": repr(data[res_id]),
        }

    def log(self, method, old_values=None, new_values=None):
        """
        The function logs changes made to a model's records by creating an audit log entry with
        information about the user, model, record, method, and data.

        :param method: The "method" parameter is a string that represents the action or method being
        logged. It could be a create, write, or delete action, for example
        :param old_values: The `old_values` parameter is a dictionary that contains the previous values
        of the fields that were changed. The keys of the dictionary are the field names, and the values
        are the old values of those fields
        :param new_values: The `new_values` parameter is a dictionary that contains the updated values
        of the fields in the record. It represents the new state of the record after the changes have
        been made
        :return: Nothing is being returned. The return statement at the end of the method is empty, so
        it returns None.
        """
        if old_values or new_values:
            fields_to_log = self.field_to_log_ids.mapped("name")
            data = self._format_data_to_log(old_values, new_values, fields_to_log)
            audit_log = self.env["spp.audit.log"].sudo()
            for rec in self:
                for res_id in data:
                    audit_log_vals = rec.get_audit_log_vals(res_id, method, data)
                    audit_log.create(audit_log_vals)
        return
