from odoo import api, models


class SppAuditRule(models.Model):
    _inherit = "spp.audit.rule"

    @api.model
    def create_rules(
        self,
        rule_name: str,
        model: str,
        fields_to_log: list,
        view_logs=True,
        log_create=True,
        log_write=True,
        log_unlink=True,
        parent_rule_name="",
        connecting_field_name="",
        **kwargs,
    ):
        rule = self.env["spp.audit.rule"].search([("name", "=", rule_name)], limit=1)

        model_id = self.env["ir.model"].search([("model", "=", model)])
        if model_id:
            field_to_log_list = []
            for field_name in fields_to_log:
                field = self.env["ir.model.fields"].search(
                    [("model_id", "=", model_id.id), ("name", "=", field_name)], limit=1
                )
                if field:
                    field_to_log_list.append((4, field.id))

            vals = {
                "name": rule_name,
                "model_id": model_id.id,
                "field_to_log_ids": field_to_log_list,
                "view_logs": view_logs,
                "log_create": log_create,
                "log_write": log_write,
                "log_unlink": log_unlink,
            }

            if parent_rule_name and connecting_field_name:
                parent_rule = self.env["spp.audit.rule"].search([("name", "=", parent_rule_name)], limit=1)
                if parent_rule:
                    connecting_field = self.env["ir.model.fields"].search(
                        [
                            ("name", "=", connecting_field_name),
                            ("model_id", "=", model_id.id),
                            ("relation", "=", parent_rule.model_id.model),
                        ]
                    )
                    if connecting_field:
                        vals.update(
                            {
                                "parent_id": parent_rule.id,
                                "field_id": connecting_field.id,
                            }
                        )

            if rule:
                rule.write(vals)
            else:
                self.env["spp.audit.rule"].create(vals)

        return
