from odoo import fields, models


class SppRegistryGroupHierarchy(models.Model):
    _inherit = "res.partner"

    is_group_hierarchy = fields.Boolean(default=False)
