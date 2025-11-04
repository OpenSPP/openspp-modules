# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class IrModelFields(models.Model):
    _inherit = "ir.model.fields"

    field_group_id = fields.Many2one(
        "spp.custom.field.group",
        string="Field Group",
        help="Group this field belongs to for UI organization",
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Order of the field within its group or section",
    )
