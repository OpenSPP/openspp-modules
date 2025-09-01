from odoo import fields, models


class ConfigParameter(models.Model):
    _inherit = "ir.config_parameter"

    hidden = fields.Boolean(
        string="Hidden", default=False, help="If checked, this parameter will be hidden in the settings UI."
    )
