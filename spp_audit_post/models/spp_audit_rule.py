import json

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SppAuditRule(models.Model):
    _inherit = "spp.audit.rule"
    _parent_name = "parent_id"
    _parent_store = True

    parent_id = fields.Many2one(
        "spp.audit.rule",
        string="Parent Rule",
        domain=[("model_id.is_mail_thread", "=", True)],
    )
    child_ids = fields.One2many("spp.audit.rule", "parent_id", string="Related Rules", readonly=True)

    is_mail_thread = fields.Boolean(related="model_id.is_mail_thread")

    # will be visible and used only if audit rule have parent
    field_id = fields.Many2one(
        "ir.model.fields",
        ondelete="cascade",
        help="Field that connects this model to the model of the parent rule.",
    )
    field_id_domain = fields.Char(
        compute="_compute_field_id_domain",
        readonly=True,
    )

    parent_path = fields.Char(index=True)

    @api.onchange("model_id")
    def _onchange_model_id(self):
        super()._onchange_model_id()
        if self.model_id:
            self.update(
                {
                    "field_id": None,
                }
            )

        return

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

    @api.constrains("parent_id", "field_id")
    def _check_model_id_field_id(self):
        for rec in self:
            if rec.parent_id and not rec.field_id:
                raise ValidationError(_("Field is required if the rule is a child rule."))
            if rec.parent_id and rec.field_id.relation != rec.parent_id.model_id.model:
                error_msg = f"Field's relation should be {rec.parent_id.model_id.name}"
                raise ValidationError(_(error_msg))

    def get_most_parent(self, res_ids):
        """
        The function `get_most_parent` retrieves the model name and ids of the most parent rule based on
        a given set of resource ids.

        :param res_ids: The `res_ids` parameter is a list of record IDs
        :return: a tuple containing the model name and a list of record IDs.
        """
        if not self.parent_id:
            return None, []

        # Initialize variable to be used in while loop
        current_rule_id = self
        parent_rule_id = self.parent_id
        currect_model_records = {"model": self.model_id.model, "ids": res_ids}

        # get the model name and ids of the most parent rule
        # loop will break if a rule doesn't have parent rule
        while parent_rule_id:
            current_records = self.env[currect_model_records["model"]].browse(currect_model_records["ids"])
            currect_model_records["model"] = parent_rule_id.model_id.model
            new_ids = []
            for record in current_records:
                new_ids.extend(getattr(record, current_rule_id.field_id.name).ids)
            currect_model_records["ids"] = new_ids

            current_rule_id = parent_rule_id
            parent_rule_id = parent_rule_id.parent_id

        return currect_model_records["model"], [str(record_id) for record_id in currect_model_records["ids"]]

    def get_audit_log_vals(self, res_id, method, data):
        result = super().get_audit_log_vals(res_id, method, data)

        parent_model, parent_res_ids = self.get_most_parent([res_id])

        result.update(
            {
                "parent_model_id": self.env["ir.model"].search([("model", "=", parent_model)], limit=1).id,
                "parent_res_ids_str": ",".join(parent_res_ids),
            }
        )

        return result
