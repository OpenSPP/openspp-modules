# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class CustomFieldGroup(models.Model):
    _name = "spp.custom.field.group"
    _description = "Custom Field Group"
    _order = "sequence, name"

    name = fields.Char(string="Group Name", required=True, translate=True)
    target_type = fields.Selection(
        selection=[("grp", "Group"), ("indv", "Individual")],
        string="Target Type",
        required=True,
        default="grp",
        help="Specify whether this group is for Group or Individual fields",
    )
    sequence = fields.Integer(string="Sequence", default=10)
    description = fields.Text(string="Description", translate=True)
    active = fields.Boolean(string="Active", default=True)
