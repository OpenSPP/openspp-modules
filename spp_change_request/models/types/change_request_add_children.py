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
    _rec_name = "registrant_id"

    registrant_id = fields.Many2one(
        "res.partner",
        "Group",
        domain=[("is_registrant", "=", True), ("is_group", "=", True)],
        required=True,
    )

    # Registrant Fields
    family_name = fields.Char(required=True)
    given_name = fields.Char(required=True)
    addl_name = fields.Char("Additional Name")
    birth_place = fields.Char()
    birthdate_not_exact = fields.Boolean()
    birthdate = fields.Date("Date of Birth")
    gender = fields.Selection(
        [("Female", "Female"), ("Male", "Male"), ("Other", "Other")],
    )
    address = fields.Text()

    # Group Membership Fields
    kind = fields.Many2many(
        "g2p.group.membership.kind", string="Group Membership Kinds"
    )
