# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import Command, _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


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
    _inherit = [
        "spp.change.request.source.mixin",
        "spp.change.request.validation.sequence.mixin",
    ]
    _description = "Add Children Change Request Type"
    _order = "id desc"

    # Initialize DMS Storage
    DMS_STORAGE = "spp_change_request.attachment_storage_add_children"

    # Redefine registrant_id to set specific domain and label
    registrant_id = fields.Many2one(
        "res.partner",
        "Add to Group",
        domain=[("is_registrant", "=", True), ("is_group", "=", True)],
    )

    request_type = fields.Selection(related="change_request_id.request_type")

    # Change Request Fields
    family_name = fields.Char()
    given_name = fields.Char()
    addl_name = fields.Char("Additional Name")
    birth_place = fields.Char()
    birthdate_not_exact = fields.Boolean()
    birthdate = fields.Date("Date of Birth")
    gender = fields.Selection(
        [("Female", "Female"), ("Male", "Male"), ("Other", "Other")],
    )
    address = fields.Text()
    kind = fields.Many2many(
        "g2p.group.membership.kind", string="Group Membership Types"
    )

    # Target Group Current Members
    group_member_ids = fields.One2many(
        "spp.change.request.group.members", "group_add_children_id", "Group Members"
    )

    # Add domain to inherited field: validation_ids
    validation_ids = fields.Many2many(
        relation="spp_change_request_add_children_rel",
        domain=[("request_type", "=", _name)],
    )

    def write(self, vals):
        res = super(ChangeRequestAddChildren, self).write(vals)
        if self.registrant_id:
            # Update the spp.change.request (base) registrant_id
            self._update_registrant_id(self)
        return res

    # @api.model_create_multi
    # @api.returns("self", lambda value: value.id)
    # def create(self, vals_list):
    #    res = super(ChangeRequestAddChildren, self).create(vals_list)
    #    return res

    @api.onchange("registrant_id")
    def _onchange_registrant_id(self):
        if self.group_member_ids:
            self.group_member_ids = [(Command.clear())]
        # Populate the group members
        self._copy_group_member_ids()

    def _copy_group_member_ids(self):
        for rec in self:
            _logger.info(
                "Change Request: Add Children _copy_group_member_ids: rec: %s" % rec
            )
            for mrec in rec.registrant_id.group_membership_ids:
                kind_ids = mrec.kind and mrec.kind.ids or None
                group_members = {
                    "group_add_children_id": rec.id,
                    "individual_id": mrec.individual.id,
                    "kind_ids": kind_ids,
                }
                self.env["spp.change.request.group.members"].create(group_members)

    def _get_name(self):
        name = ""
        if self.family_name:
            name += self.family_name + ", "
        if self.given_name:
            name += self.given_name + " "
        if self.addl_name:
            name += self.addl_name + " "
        return name.title()

    def _update_live_data(self):
        self.ensure_one()
        # Create a new individual (res.partner)
        kinds = []
        for rec in self.kind:
            kinds.append(Command.link(rec.id))
        individual_id = self.env["res.partner"].create(
            {
                "is_registrant": True,
                "is_group": False,
                "name": self._get_name(),
                "family_name": self.family_name,
                "given_name": self.given_name,
                "addl_name": self.addl_name,
                "birth_place": self.birth_place,
                "birthdate_not_exact": self.birthdate_not_exact,
                "birthdate": self.birthdate,
                "gender": self.gender,
                "address": self.address,
            }
        )
        # Add to group
        self.env["g2p.group.membership"].create(
            {
                "group": self.registrant_id.id,
                "individual": individual_id.id,
                "kind": kinds,
            }
        )

    def _on_validate(self, request):
        self.ensure_one()
        # Get current validation sequence
        stage, message, validator_id = request._get_validation_stage()
        if stage:
            validator = {
                "stage_id": stage.id,
                "validator_id": validator_id,
                "date_validated": fields.Datetime.now(),
            }
            vals = {
                "validator_ids": [(Command.create(validator))],
                "validatedby_id": validator_id,
                "date_validated": fields.Datetime.now(),
            }
            if message == "FINAL":
                # Mark previous activity as 'done'
                request.last_activity_id.action_done()
                # Create apply changes activity
                activity_type = "spp_change_request.apply_changes_activity"
                summary = _("For Application of Changes")
                note = _(
                    "The change request is now fully validated. It is now submitted "
                    + "for final application of changes."
                )
                activity = request._generate_activity(activity_type, summary, note)

                vals.update(
                    {
                        "state": "validated",
                        "last_activity_id": activity.id,
                    }
                )
            # Update the change request
            request.update(vals)
        else:
            raise ValidationError(message)

    def open_registrant_details_form(self):
        self.ensure_one()
        res_id = self.registrant_id.id
        form_id = self.env.ref("g2p_registry_group.view_groups_form").id
        action = self.env["res.partner"].get_formview_action()
        context = {
            "create": False,
            "edit": False,
        }
        action.update(
            {
                "name": _("Group Details"),
                "views": [(form_id, "form")],
                "res_id": res_id,
                "target": "new",
                "context": context,
                "flags": {"mode": "readonly"},
            }
        )
        return action
