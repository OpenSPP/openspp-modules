# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ChangeRequestTypeCustomAddChildren(models.Model):
    _inherit = "spp.change.request"

    @api.model
    def _selection_request_type_ref_id(self):
        selection = super()._selection_request_type_ref_id()
        new_request_type = ("spp.change.request.add.children", "Add Children")
        if new_request_type not in selection:
            selection.append(new_request_type)
        return selection


class ChangeRequestAddChildren(models.Model):
    _name = "spp.change.request.add.children"
    _inherit = "spp.change.request.source.mixin"
    _description = "Add Children Change Request Type"
    _rec_name = "group_id"

    group_id = fields.Many2one(
        "res.partner", "Group", domain=[("is_group", "=", True)], required=True
    )
    children_ids = fields.Many2many(
        "res.partner", string="Children to be added to group"
    )
