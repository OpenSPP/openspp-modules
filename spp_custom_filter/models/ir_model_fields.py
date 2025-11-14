from odoo import fields, models


class IrModelFields(models.Model):
    _inherit = ["ir.model.fields"]

    allow_filter = fields.Boolean(
        string="Show on Custom Filter",
        default=False,
        help="Allow to show this field on Custom filter!",
    )
    filter_target = fields.Selection(
        [("both", "Both"), ("group", "Group"), ("individual", "Individual")],
        string="Filter Target",
        default="both",
    )

    def _reflect_field_params(self, field, model_id):
        vals = super()._reflect_field_params(field, model_id)
        vals["allow_filter"] = getattr(field, "allow_filter", False)
        vals["filter_target"] = getattr(field, "filter_target", "both")
        return vals

    def _instanciate_attrs(self, field_data):
        attrs = super()._instanciate_attrs(field_data)
        if attrs and field_data.get("allow_filter"):
            attrs["allow_filter"] = field_data["allow_filter"]
        if attrs and field_data.get("filter_target"):
            attrs["filter_target"] = field_data["filter_target"]
        return attrs
