# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from odoo import Command, _, fields, models
from odoo.exceptions import UserError, ValidationError


class ChangeRequestSourceMixin(models.AbstractModel):
    """Change Request Data Source mixin."""

    _name = "spp.change.request.source.mixin"
    _description = "Change Request Data Source Mixin"
    _rec_name = "change_request_id"

    required_document_type = []

    registrant_id = fields.Many2one(
        "res.partner", "Registrant", domain=[("is_registrant", "=", True)]
    )
    applicant_id = fields.Many2one(
        "res.partner",
        "Applicant",
        domain=[("is_registrant", "=", True), ("is_group", "=", False)],
    )
    applicant_phone = fields.Char(
        "Applicant's Phone Number", related="change_request_id.applicant_phone"
    )
    change_request_id = fields.Many2one(
        "spp.change.request", "Change Request", required=True
    )
    assign_to_id = fields.Many2one(
        "res.users", "Assigned to", related="change_request_id.assign_to_id"
    )
    last_validated_by_id = fields.Many2one(
        "res.users", "Last Validator", related="change_request_id.last_validated_by_id"
    )
    date_validated = fields.Datetime(related="change_request_id.date_validated")
    state = fields.Selection(
        related="change_request_id.state",
        string="Status",
        readonly=True,
    )

    # Target Fields
    group_address = fields.Text(related="registrant_id.address", readonly=True)
    group_registration_date = fields.Date(
        related="registrant_id.registration_date", readonly=True
    )

    # DMS Field
    dms_directory_ids = fields.One2many(
        "dms.directory",
        "res_id",
        string="DMS Directories",
        domain=lambda self: [
            ("res_model", "=", self._name),
            ("storage_id.save_type", "!=", "attachment"),
        ],
        auto_join=True,
    )

    def _update_registrant_id(self, res):
        for rec in res:
            if rec.registrant_id:
                rec.change_request_id.update({"registrant_id": rec.registrant_id.id})

    def get_request_type_view_id(self):
        """
        Retrieve form view ID.
        :param self: The request.
        :return: form view ID
        """
        return (
            self.env["ir.ui.view"]
            .sudo()
            .search([("model", "=", self._name), ("type", "=", "form")], limit=1)
            .id
        )

    def update_live_data(self):
        """
        This method is used to apply the changes to models based on the type of change request.
        :param self: The request.
        :return:
        """
        raise NotImplementedError()

    def validate_data(self):
        """
        This method is used to validate the data of the change request before submitting for review.
        :param self: The request.
        :return:
        :raises:
            ValidationError: Exception raised when something is not valid.
        """
        self.ensure_one()
        for document_type in self.required_document_type:
            # TODO: Check the required documents
            if True:
                raise ValidationError(
                    _("Please upload the required document type: %s", document_type)
                )

    def on_submit(self):
        for rec in self:
            rec._on_submit(rec.change_request_id)

    def _on_submit(self, request):
        """
        This method is used to submit the change request.
        :param self: The request type.
        :param request: The request.
        :return:
        """
        self.ensure_one()
        if request.state == "draft":
            # Validate the submitted data
            self.validate_data()
            # Mark previous activity as 'done'
            request.last_activity_id.action_done()
            # Create validation activity
            activity_type = "spp_change_request.validation_activity"
            summary = _("For Validation")
            note = _(
                "The change request is now set for validation. Depending on the "
                + "validation sequence, this may be subjected to one or more validations."
            )
            activity = request._generate_activity(activity_type, summary, note)

            # Update change request
            request.update(
                {
                    "date_requested": fields.Datetime.now(),
                    "state": "pending",
                    "last_activity_id": activity.id,
                    "assign_to_id": None,
                }
            )
        else:
            raise UserError(
                _("The request must be in draft state to be set to pending validation.")
            )

    def on_validate(self):
        for rec in self:
            rec._on_validate(rec.change_request_id)

    def _on_validate(self, request):
        self.ensure_one()
        # Check if CR is assigned to current user
        if request._check_user("Validate"):
            if request.state == "pending":
                # Get current validation sequence
                stage, message, validator_id = request._get_validation_stage()
                if stage:
                    validator = {
                        "stage_id": stage.stage_id.id,
                        "validator_id": validator_id,
                        "date_validated": fields.Datetime.now(),
                    }
                    vals = {
                        "validator_ids": [(Command.create(validator))],
                        "last_validated_by_id": validator_id,
                        "date_validated": fields.Datetime.now(),
                        "assign_to_id": None,
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
                        activity = request._generate_activity(
                            activity_type, summary, note
                        )

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
            else:
                raise ValidationError(
                    _("The request to be validated must be in submitted state.")
                )

    def apply(self):
        for rec in self:
            rec._apply(rec.change_request_id)

    def _apply(self, request):
        """
        This method is used to apply the change request.
        :param self: The request type.
        :param request: The request.
        :return:
        """
        self.ensure_one()
        # Check if CR is assigned to current user
        if request._check_user("Apply"):
            if request.state == "validated":
                # Apply Changes to Live Data
                self.update_live_data()
                # Update CR record
                request.update(
                    {
                        "applied_by_id": self.env.user,
                        "date_applied": fields.Datetime.now(),
                        "state": "applied",
                    }
                )
                # Mark previous activity as 'done'
                request.last_activity_id.action_done()
            else:
                raise ValidationError(
                    _(
                        "The request must be in validated state for changes to be applied."
                    )
                )

    def on_reject(self):
        for rec in self:
            rec._on_reject(rec.change_request_id)

    def _on_reject(self, request):
        """
        This method is used to reject the change request.
        :param self: The request type.
        :param request: The request.
        :return:
        """
        self.ensure_one()
        # Check if CR is assigned to current user
        if request._check_user("Reject"):
            if request.state in ("draft", "pending"):
                request.update(
                    {
                        "state": "rejected",
                    }
                )
                # Mark previous activity as 'done'
                request.last_activity_id.action_done()
            else:
                raise UserError(
                    _(
                        "The request to be rejected must be in draft or pending validation state."
                    )
                )

    def _copy_group_member_ids(self, group_id_field):
        for rec in self:
            for mrec in rec.registrant_id.group_membership_ids:
                kind_ids = mrec.kind and mrec.kind.ids or None
                group_members = {
                    group_id_field: rec.id,
                    "individual_id": mrec.individual.id,
                    "kind_ids": kind_ids,
                }
                self.env["spp.change.request.group.members"].create(group_members)

    def _copy_service_point_ids(self, change_request_field):
        for rec in self:
            for mrec in rec.registrant_id.service_point_ids:
                service_points = {
                    change_request_field: rec.id,
                    "service_point_id": mrec.id,
                }
                self.env["pds.change.request.service.point"].create(service_points)

    def _copy_from_group_member_ids(self, group_ref_field, group_id_field):
        for rec in self:
            for mrec in rec[group_ref_field].group_membership_ids:
                kind_ids = mrec.kind and mrec.kind.ids or None
                if (
                    kind_ids
                    and self.env.ref(
                        "g2p_registry_membership.group_membership_kind_head"
                    ).id
                    not in kind_ids
                ) or not kind_ids:
                    group_members = {
                        group_id_field: rec.id,
                        "individual_id": mrec.individual.id,
                        "kind_ids": kind_ids,
                        "new_relation_to_head": None,
                    }
                    self.env["pds.change.request.src.grp"].create(group_members)

    def open_applicant_details_form(self):
        self.ensure_one()
        res_id = self.applicant_id.id
        form_id = self.env.ref("g2p_registry_individual.view_individuals_form").id
        action = self.env["res.partner"].get_formview_action()
        context = {
            "create": False,
            "edit": False,
        }
        action.update(
            {
                "name": _("Applicant Details"),
                "views": [(form_id, "form")],
                "res_id": res_id,
                "target": "new",
                "context": context,
                "flags": {"mode": "readonly"},
            }
        )
        return action

    def open_user_assignment_wiz(self):
        for rec in self:
            assign_self = False
            if rec.change_request_id.assign_to_id:
                if rec.change_request_id.assign_to_id.id != self.env.user.id:
                    assign_self = True
            else:
                assign_self = True
            if not assign_self:
                form_id = self.env.ref(
                    "spp_change_request.change_request_user_assign_wizard"
                ).id
                action = {
                    "name": _("Assign Change Request to User"),
                    "type": "ir.actions.act_window",
                    "view_mode": "form",
                    "view_id": form_id,
                    "view_type": "form",
                    "res_model": "spp.change.request.user.assign.wizard",
                    "target": "new",
                    "context": {
                        "curr_assign_to_id": rec.change_request_id.assign_to_id.id,
                        "change_request_id": rec.change_request_id.id,
                    },
                }
                return action
            else:
                self.change_request_id.assign_to_user(self.env.user)
