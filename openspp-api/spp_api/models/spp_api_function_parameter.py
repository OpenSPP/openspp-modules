from odoo import api, fields, models


class SPPAPIFunctionParameter(models.Model):
    """
    OpenAPI Function Parameter Model
    """

    _name = "spp_api.function.parameter"
    _description = "OpenAPI Function"

    path_id = fields.Many2one("spp_api.path", required=True, ondelete="cascade")
    name = fields.Char(required=True)
    sequence = fields.Integer()
    type = fields.Selection(
        [
            ("integer", "Integer"),
            ("float", "Float"),
            ("boolean", "Boolean"),
            ("string", "String"),
            ("array", "Array"),
            ("object", "Object (Dictionary)"),
        ],
        required=True,
    )
    description = fields.Char()
    required = fields.Boolean()
    default_value = fields.Char()

    @api.onchange("default_value")
    def _onchange_default_value(self):
        """
        Update the 'required' field based on the presence of a default value.
        """
        if self.default_value:
            self.required = False

    @api.onchange("required")
    def _onchange_required(self):
        """
        Update the 'required' field based on the presence of a default value.
        """
        if self.default_value:
            self.required = False
