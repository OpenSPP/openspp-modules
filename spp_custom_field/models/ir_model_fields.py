# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class IrModelFields(models.Model):
    _inherit = "ir.model.fields"

    field_group_id = fields.Many2one(
        "spp.custom.field.group",
        string="Field Group",
        help="Group this field belongs to for UI organization",
        domain="[('target_type', '=', target_type)]",
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Order of the field within its group or section",
    )

    @api.onchange("target_type")
    def _onchange_target_type(self):
        """Clear field_group_id if target_type changes and doesn't match"""
        if self.field_group_id and self.field_group_id.target_type != self.target_type:
            self.field_group_id = False
