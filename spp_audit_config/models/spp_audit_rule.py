from odoo import api, models


class SppAuditRule(models.Model):
    _inherit = "spp.audit.rule"

    @api.model
    @api.returns("self", lambda value: value.id)
    def create_rules(self, vals):
        # Used in creation of rules when installing or upgrading this module
        model_id = vals.get("model_id")
        parent_id = vals.get("parent_id")

        # to avoid sql constraints error when upgrading this module
        if model_id and parent_id:
            rule = self.env["spp.audit.rule"].search(
                [
                    ("model_id", "=", model_id),
                    ("parent_id", "=", parent_id),
                ],
                limit=1,
            )
            if rule:
                return rule

        return self.env["spp.audit.rule"].create(vals)
