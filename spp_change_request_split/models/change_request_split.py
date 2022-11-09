# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import json
import logging

from odoo import Command, _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ChangeRequestTypeCustomSplit(models.Model):
    _inherit = "spp.change.request"

    @api.model
    def _selection_request_type_ref_id(self):
        selection = super()._selection_request_type_ref_id()
        new_request_type = ("spp.change.request.split", "Split Members")
        if new_request_type not in selection:
            selection.append(new_request_type)
        return selection


class ChangeRequestSplit(models.Model):
    _name = "spp.change.request.split"
    _inherit = [
        "spp.change.request.source.mixin",
        "spp.change.request.validation.sequence.mixin",
    ]
    _description = "Split Member Change Request Type"

    # Initialize DMS Storage
    DMS_STORAGE = "spp_change_request_split.attachment_storage_split"

    # Redefine registrant_id to set specific domain and label
    registrant_id = fields.Many2one(
        "res.partner",
        "Split Member of Group",
        domain=[("is_registrant", "=", True), ("is_group", "=", True)],
    )

    request_type = fields.Selection(related="change_request_id.request_type")

    # Change Request Fields
    registrant_to_split_id = fields.Many2one(
        "res.partner",
        "Individual to Split",
        domain=[("is_registrant", "=", True), ("is_group", "=", False)],
    )
    # For dynamic domain based on registrant_id.group_membership_ids
    registrant_to_split_id_domain = fields.Char(
        compute="_compute_registrant_to_split_id_domain",
        readonly=True,
        store=False,
    )

    new_registrant_id = fields.Many2one(
        "res.partner",
        "Destination Group",
        domain=[("is_registrant", "=", True), ("is_group", "=", True)],
    )

    # Target Group Current Members
    split_group_member_ids = fields.One2many(
        "spp.change.request.group.members", "group_to_split_id", "Group Members"
    )

    # Add domain to inherited field: validation_ids
    validation_ids = fields.Many2many(
        relation="spp_change_request_split_rel", domain=[("request_type", "=", _name)]
    )

    def write(self, vals):
        res = super(ChangeRequestSplit, self).write(vals)
        if self.registrant_id:
            # Must update the spp.change.request (base) registrant_id
            self._update_registrant_id(self)
        self._copy_group_member_ids()
        return res

    @api.onchange("registrant_id")
    def _onchange_registrant_id(self):
        if self.split_group_member_ids:
            self.update(
                {
                    "registrant_to_split_id": None,
                    "split_group_member_ids": [(Command.clear())],
                }
            )

    def _copy_group_member_ids(self):
        for rec in self:
            _logger.info(
                "Change Request: Split Member _copy_group_member_ids: rec: %s" % rec
            )
            for mrec in rec.registrant_id.group_membership_ids:
                kind_ids = mrec.kind and mrec.kind.ids or None
                group_members = {
                    "group_to_split_id": rec.id,
                    "individual_id": mrec.individual.id,
                    "kind_ids": kind_ids,
                }
                self.env["spp.change.request.group.members"].create(group_members)

    @api.depends("registrant_id")
    def _compute_registrant_to_split_id_domain(self):
        for rec in self:
            domain = [("is_registrant", "=", True), ("is_group", "=", False)]
            group_membership_ids = []
            if rec.registrant_id:
                group_membership_ids = [
                    grp.individual.id for grp in rec.registrant_id.group_membership_ids
                ]
            if group_membership_ids:
                domain.append(("id", "in", group_membership_ids))
            rec.registrant_to_split_id_domain = json.dumps(domain)

    def _update_live_data(self):
        # TODO: update live data
        self.ensure_one()

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
                "name": _("Member Details"),
                "views": [(form_id, "form")],
                "res_id": res_id,
                "target": "new",
                "context": context,
                "flags": {"mode": "readonly"},
            }
        )
        return action

    def open_new_registrant_details_form(self):
        self.ensure_one()
        res_id = self.new_registrant_id.id
        form_id = self.env.ref("g2p_registry_group.view_groups_form").id
        action = self.env["res.partner"].get_formview_action()
        context = {
            "create": False,
            "edit": False,
        }
        action.update(
            {
                "name": _("Member Details"),
                "views": [(form_id, "form")],
                "res_id": res_id,
                "target": "new",
                "context": context,
                "flags": {"mode": "readonly"},
            }
        )
        return action
