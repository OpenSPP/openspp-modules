# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class OpenSPPCustomFieldsUI(models.Model):
    _inherit = "ir.model.fields"

    field_weight = fields.Float("Weight", default=0)
    with_weight = fields.Boolean(default=False)
