# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class ChangeRequestSourceMixin(models.AbstractModel):
    """Change Request Data Source mixin."""

    _name = "spp.change.request.source.mixin"
    _description = "Change Request Data Source Mixin"
    _rec_name = "change_request_id"

    REQUIRED_DOCUMENT_TYPE = []
    AUTO_APPLY_CHANGES = True

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
    dms_file_ids = fields.One2many(
        "dms.file",
        "res_id",
        string="DMS Files",
        domain=lambda self: [
            ("directory_id.res_model", "=", self._name),
            ("storage_id.save_type", "!=", "attachment"),
        ],
        auto_join=True,
    )

    current_user_assigned = fields.Boolean(
        compute="_compute_current_user_assigned", default=False
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
                "validation sequence, this may be subjected to one or more validations."
            )
            activity = request._generate_activity(activity_type, summary, note)

            # Update change request
            request.update(
                {
                    "date_requested": fields.Datetime.now(),
                    "state": "pending",
                    "last_activity_id": activity.id,
                    "assign_to_id": None,
                    "rejected_by_id": None,
                    "date_rejected": None,
                    "rejected_remarks": None,
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
        if request._check_user("Validate", auto_assign=True):
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

                    # Update the live data if the user has the access
                    if self.AUTO_APPLY_CHANGES and message == "FINAL":
                        try:
                            self.apply()
                        except UserError:
                            # Silently ignore and leave the change request as is until someone with the correct access
                            # can apply the changes
                            logging.info(
                                "User %s does not have access to apply changes."
                                % self.env.user
                            )
                            # revert the assignment if the apply failed
                            request.update({"assign_to_id": None})
                else:
                    raise ValidationError(message)
            else:
                raise ValidationError(
                    _("The request to be validated must be in submitted state.")
                )
        return

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
        if request._check_user("Apply", auto_assign=True):
            if request.state == "validated":
                # Apply Changes to Live Data
                self.update_live_data()
                # Update CR record
                request.update(
                    {
                        "applied_by_id": self.env.user,
                        "date_applied": fields.Datetime.now(),
                        "assign_to_id": None,
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
            form_id = self.env.ref("spp_change_request.change_request_reject_wizard").id
            action = {
                "name": _("Reject Change Request"),
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "view_id": form_id,
                "view_type": "form",
                "res_model": "spp.change.request.reject.wizard",
                "target": "new",
                "context": {
                    "change_request_id": rec.change_request_id.id,
                },
            }
            return action

    def _on_reject(self, request, rejected_remarks):
        """
        This method is used to reject the change request.
        :param self: The request type.
        :param request: The request.
        :return:
        """
        self.ensure_one()
        # Check if CR is assigned to current user
        if request._check_user("Reject", auto_assign=True):
            if request.state in ("draft", "pending"):
                request.update(
                    {
                        "state": "draft",
                        "rejected_remarks": rejected_remarks,
                        "rejected_by_id": self.env.user.id,
                        "date_rejected": fields.Datetime.now(),
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

    def _copy_group_member_ids(self, group_id_field, group_ref_field="registrant_id"):
        for rec in self:
            for mrec in rec[group_ref_field].group_membership_ids:
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
            "hide_from_cr": 1,
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

    def open_user_assignment_to_wiz(self):
        for rec in self:
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
                    "assign_to": True,
                },
            }
            return action

    @api.depends("assign_to_id")
    def _compute_current_user_assigned(self):
        for rec in self:
            rec.current_user_assigned = False
            if self.env.context.get("uid", False) == rec.assign_to_id.id:
                rec.current_user_assigned = True

    def check_required_documents(self):
        for directories in self.dms_directory_ids:
            file_ids_child = []

            if directories.child_directory_ids:
                for child_directories in directories.child_directory_ids:
                    file_ids_child = child_directories.file_ids.mapped("category_id.id")

            file_ids = directories.file_ids.mapped("category_id.id")
            for child_ids in file_ids_child:
                file_ids.append(child_ids)

            missing_docs = []

            for doc in self.REQUIRED_DOCUMENT_TYPE:
                document = self.env.ref(doc)
                if document.id not in file_ids:
                    missing_docs.append(document.name)

            if missing_docs:
                if len(missing_docs) > 1:
                    return _(
                        "The required documents %s are missing.",
                        ", ".join(missing_docs),
                    )
                else:
                    return _(
                        "The required document %s is missing.",
                        ", ".join(missing_docs),
                    )

        return None

    def attach_documents(self):
        for rec in self:
            # TODO: Get the directory_id based on document type
            # Get the first directory for now
            if rec.dms_directory_ids:
                directory_id = rec.dms_directory_ids[0].id
                if self.env.context.get("category_id"):
                    category_id = self.env.context.get("category_id")
                    category = self.env["dms.category"].search(
                        [("id", "=", category_id)]
                    )
                    if category:
                        form_id = self.env.ref(
                            "spp_change_request.view_dms_file_spp_custom_form"
                        ).id
                        action = {
                            "name": _("Upload Document: %s", category.name),
                            "type": "ir.actions.act_window",
                            "view_mode": "form",
                            "view_id": form_id,
                            "view_type": "form",
                            "res_model": "dms.file",
                            "target": "new",
                            "context": {
                                "default_directory_id": directory_id,
                                "default_category_id": category_id,
                            },
                        }
                        return action
                    else:
                        raise UserError(
                            _("The required document category is not configured.")
                        )
                else:
                    raise UserError(
                        _("The document category must be specified in the context.")
                    )
            else:
                raise UserError(
                    _("There are no directories defined for this change request.")
                )
