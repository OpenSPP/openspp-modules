from odoo import api, models


class SppAuditRule(models.Model):
    _inherit = "spp.audit.rule"

    @api.model
    @api.returns("self", lambda value: value.id)
    def create_rules(self, vals):
        """
        The function creates rules for installing or upgrading a module, avoiding SQL constraints
        errors.

        :param vals: The parameter "vals" is a dictionary that contains the values to be used for
        creating or updating a record in the "spp.audit.rule" model. It may contain the following keys:
        :return: The method is returning an instance of the "spp.audit.rule" model.
        """

        model_id = vals.get("model_id")
        parent_id = vals.get("parent_id")
        field_id = vals.get("field_id")

        if model_id:
            rule = self.env["spp.audit.rule"].search(
                [
                    ("model_id", "=", model_id),
                    ("parent_id", "=", parent_id),
                    ("field_id", "=", field_id),
                ],
                limit=1,
            )
            if rule:
                return rule

        return self.env["spp.audit.rule"].create(vals)
