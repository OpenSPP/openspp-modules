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

    request_type = fields.Selection(related="change_request_id.request_type")

    # Registrant Fields
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

    # Group Membership Fields
    kind = fields.Many2many(
        "g2p.group.membership.kind", string="Group Membership Kinds"
    )

    # Registry fields
    group_member_ids = fields.One2many(
        "spp.group.members.temp",
        "group_add_children_id",
        "Group Members",
        compute="_compute_group_member_ids",
        store=False,
    )

    # Add domain to inherited field: validation_ids
    validation_ids = fields.Many2many(domain=[("request_type", "=", _name)])

    def _compute_group_member_ids(self):
        for rec in self:
            if rec.registrant_id:
                rec.group_member_ids = Command.clear()
                for mrec in rec.registrant_id.group_membership_ids:
                    kind_ids = mrec.kind and mrec.kind.ids or None
                    group_members = {
                        "group_add_children_id": rec.id,
                        "individual_id": mrec.individual.id,
                        "kind_ids": kind_ids,
                        "start_date": mrec.start_date,
                        "end_date": mrec.end_date,
                    }
                    # group_member_ids.append(Command.create(group_members))
                    self.env["spp.group.members.temp"].create(group_members)
                # _logger.info(
                #    "Change Request: _compute_group_member_ids: group_member_ids = %s"
                #    % group_member_ids
                # )
                # rec.group_member_ids = group_member_ids

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
