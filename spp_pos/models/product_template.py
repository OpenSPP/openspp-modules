# Part of Newlogic OpenSPP. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ProductTemplateCustom(models.Model):
    _inherit = "product.template"

    is_locked = fields.Boolean(string="Locked", default=False)
