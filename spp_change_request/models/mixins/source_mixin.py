# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from odoo import Command, _, fields, models
from odoo.exceptions import ValidationError


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

    def on_submit(self):
        for rec in self:
            rec._on_submit(rec.change_request_id)

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

    def _on_submit(self, request):
        """
        This method is used to submit the change request.
        :param self: The request type.
        :param request: The request.
        :return:
        """
        self.ensure_one()
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

    def on_validate(self):
        for rec in self:
            rec._on_validate(rec.change_request_id)

    def _on_validate(self, request):
        self.ensure_one()
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
        request.update(
            {
                "state": "rejected",
            }
        )
        # Mark previous activity as 'done'
        request.last_activity_id.action_done()

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
                        "new_relation_to_head": mrec.individual.relation_to_head.id,
                        "new_birthdate": mrec.individual.birthdate,
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
