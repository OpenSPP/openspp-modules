# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import json
import logging

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from odoo.addons.phone_validation.tools import phone_validation

_logger = logging.getLogger(__name__)


class ChangeRequestBase(models.Model):
    """
    ChangeRequestBase is the base model for all change requests.
    The object containing the change request details points to this model.

    Every change requests have a DMS folder associated where the documents are stored.

    The change request is assigned to a user who is responsible for the change request.

    A change request can be only deleted if it is in draft state and by its original submitter.

    The change request status can evolve as follows:

    .. graphviz::

       digraph {
          "draft" -> "pending";
          "draft" -> "cancelled";
          "pending" -> "validated";
          "validated" -> "validated";
          "validated" -> "applied";
          "validated" -> "rejected";
          "rejected" -> "pending";
          "rejected" -> "draft";
          "rejected" -> "cancelled";
       }

    """

    _name = "spp.change.request"
    _description = "Change Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"
    _check_company_auto = True

    def _default_name(self):
        name = self.env["ir.sequence"].next_by_code("spp.change.request.num")
        return name

    name = fields.Char("Request #", required=True, default=_default_name)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    date_requested = fields.Datetime()  # Date the change request was submitted
    request_type = fields.Selection(
        selection="_selection_request_type_ref_id", required=True
    )
    registrant_id = fields.Many2one(
        "res.partner",
        "Registrant",
        domain=[("is_registrant", "=", True)],
    )  #: Registrant who submitted the change request

    # For ID Scanner Widget
    id_document_details = fields.Text("Scanned ID Document")
    # For QR Code Scanner Widget
    qr_code_details = fields.Text("Scanned QR Card")

    applicant_id = fields.Many2one(
        "res.partner",
        "Applicant",
        domain=[("is_registrant", "=", True), ("is_group", "=", False)],
    )  #: Applicant who submitted the change request (In case the registrant is a group, the applicant is the individual)
    applicant_id_domain = fields.Char(
        compute="_compute_applicant_id_domain",
        readonly=True,
        store=False,
    )
    applicant_phone = fields.Char(
        "Applicant's Phone Number"
    )  #: Applicant's phone number

    request_type_ref_id = fields.Reference(
        string="Change Request Template", selection="_selection_request_type_ref_id"
    )
    validator_ids = fields.One2many(
        "spp.change.request.validators", "request_id", "Validation Records"
    )  #: List of validators that validated the change request
    assign_to_id = fields.Many2one("res.users", "Assigned to")  #: current assigned user
    last_validated_by_id = fields.Many2one(
        "res.users", "Validated by"
    )  #: last user that validated the change request
    date_validated = (
        fields.Datetime()
    )  #: last date the change request has been validated

    # TODO: Record the next validation sequence and area center
    next_validation_sequence_id = fields.Many2one(
        "spp.change.request.validation.sequence", "Next Validation Sequence"
    )  #: When the change request is pending validation, this store the next required validation in the sequence

    # TODO: @edwin: remove `center` from this variable name
    next_area_center_ids = fields.Many2many(
        "spp.area", string="Next Area"
    )  #: When the change request change the area, we store the destination in case a validation based on it is required

    applied_by_id = fields.Many2one(
        "res.users", "Applied by"
    )  #: user that applied the change request
    date_applied = fields.Datetime()  #: date the change request was applied
    rejected_by_id = fields.Many2one(
        "res.users", "Rejected by"
    )  #: user that rejected the change request
    date_rejected = fields.Datetime()  #: date the change request was rejected
    rejected_remarks = fields.Text(
        "Rejection Remarks"
    )  #: remarks of why the change request was rejected

    last_activity_id = fields.Many2one("mail.activity")

    # TODO: @edwin: can we rename this status?
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending", "Pending Validation"),
            ("validated", "Validated"),
            ("applied", "Applied"),
            ("rejected", "Rejected"),
            ("cancelled", "Cancelled"),
        ],
        "Status",
        required=True,
        readonly=True,
        default="draft",
    )  #: status of the change request

    cancelled_by_id = fields.Many2one(
        "res.users", "Cancelled by"
    )  #: user that cancelled the change request
    date_cancelled = fields.Datetime()  #: date the change request was cancelled

    reset_to_draft_by_id = fields.Many2one(
        "res.users", "Cancelled by"
    )  #: user that reset the change request to draft
    date_reset_to_draft = (
        fields.Datetime()
    )  #: date the change request was reset to draft

    validation_group_id = fields.Many2one(
        "res.groups",
        string="Change Request Validation Group",
        compute="_compute_validation_group_id",
        store=True,
    )
    hide_button_css = fields.Html(
        string="CSS", sanitize=False, compute="_compute_hide_button_css", store=False
    )

    @api.depends("state")
    def _compute_hide_button_css(self):
        for record in self:
            if (
                record.state == "draft"
                and record.create_uid != self.env.user
                and record.assign_to_id != self.env.user
            ):
                # Hide edit button when state is 'draft' and current user is not in either create_uid or assign_to_id
                record.hide_button_css = (
                    "<style>.o_form_button_edit {display: none !important;}</style>"
                )
            else:
                record.hide_button_css = "<style></style>"

    @api.model
    def create(self, vals):

        # Assign the CR to the current user by default
        if "assign_to_id" not in vals or vals["assign_to_id"] is None:
            vals["assign_to_id"] = self.env.user.id
        res = super(ChangeRequestBase, self).create(vals)
        # Create pending validation activity
        activity_type = "spp_change_request.pending_validation_activity"
        summary = _("For Pending Validation")
        note = _(
            "A new change request was submitted. The next step will set this request to 'Pending Validation'."
        )
        activity = res._generate_activity(activity_type, summary, note)
        res["last_activity_id"] = activity.id
        return res

    def unlink(self):
        for rec in self:
            # Only allow the deletion of draft change requests by the user who created it
            if rec.state == "draft" and rec.create_uid == self.env.user:
                # Remove the associated CR type record
                rec.request_type_ref_id.unlink()
                return super(ChangeRequestBase, self).unlink()
            else:
                raise UserError(
                    _("Only draft change requests can be deleted by its creator.")
                )

    @api.model
    def _selection_request_type_ref_id(self):
        return []

    @api.depends("registrant_id")
    def _compute_applicant_id_domain(self):
        for rec in self:
            domain = [("id", "=", 0)]
            if rec.registrant_id:
                group_membership_ids = rec.registrant_id.group_membership_ids.mapped(
                    "individual.id"
                )
                domain = [("id", "in", group_membership_ids)]
            rec.applicant_id_domain = json.dumps(domain)

    @api.onchange("registrant_id")
    def _onchange_registrant_id(self):
        if self.registrant_id:
            self.update(
                {
                    "applicant_id": None,
                    "applicant_phone": None,
                }
            )

    @api.onchange("applicant_id")
    def _onchange_applicant_id(self):
        if self.applicant_id:
            vals = {
                "applicant_phone": self.applicant_id.phone,
            }
        else:
            vals = {
                "applicant_phone": None,
            }
        self.update(vals)

    @api.constrains("registrant_id", "applicant_phone")
    def _check_applicant_phone(self):
        for rec in self:
            country_code = (
                rec.registrant_id.country_id.code
                if rec.registrant_id
                and rec.registrant_id.country_id
                and rec.registrant_id.country_id.code
                else None
            )
            if country_code is None:
                country_code = (
                    rec.company_id.country_id.code
                    if rec.company_id.country_id and rec.company_id.country_id.code
                    else None
                )
            if rec.applicant_phone:
                try:
                    phone_validation.phone_parse(rec.applicant_phone, country_code)
                except UserError as e:
                    raise ValidationError(_("Incorrect phone number format")) from e

    @api.onchange("id_document_details")
    def _onchange_scan_id_document_details(self):
        if self.id_document_details:
            try:
                details = json.loads(self.id_document_details)
            except json.decoder.JSONDecodeError as e:
                details = None
                _logger.error(e)
            if details:
                if self.registrant_id:
                    group_membership_ids = (
                        self.registrant_id.group_membership_ids.mapped("individual.id")
                    )
                    domain = [
                        ("partner_id", "in", group_membership_ids),
                        ("value", "=", details["document_number"].strip()),
                    ]
                    id_docs = self.env["g2p.reg.id"].search(domain)
                    if id_docs:
                        vals = {
                            "applicant_id": id_docs[0].partner_id.id,
                            "applicant_phone": id_docs[0].partner_id.phone,
                        }
                        self.update(vals)
                    else:
                        raise UserError(
                            _(
                                "There are no registrant found with the ID number scanned."
                            )
                        )
                else:
                    raise UserError(_("A group must be selected."))
            else:
                raise UserError(_("There are no data captured from the ID scanner."))

    @api.onchange("qr_code_details")
    def _onchange_scan_qr_code_details(self):
        if self.qr_code_details:
            try:
                details = json.loads(self.qr_code_details)
            except json.decoder.JSONDecodeError as e:
                details = None
                _logger.error(e)
            if details:
                domain = [
                    ("partner_id.is_registrant", "=", True),
                    ("partner_id.is_group", "=", True),
                    ("value", "=", details["qrcode"].strip()),
                ]
                id_docs = self.env["g2p.reg.id"].search(domain)
                if id_docs:
                    vals = {
                        "registrant_id": id_docs.partner_id[0].id,
                    }
                    self.update(vals)
                else:
                    raise UserError(
                        _(
                            "There are no group found with the ID number from the QR Code scanned."
                        )
                    )
            else:
                raise UserError(
                    _("There are no data captured from the QR Code scanner.")
                )

    def open_change_request_form(self, target="current", mode="readonly"):
        self.ensure_one()
        if self.request_type_ref_id:
            # Get the res_model and res_id from the request_type_ref_id (reference field)
            request_type_ref_id = str(self.request_type_ref_id)
            s = request_type_ref_id.find("(")
            res_model = request_type_ref_id[:s]
            res_id = self.request_type_ref_id.id
            if res_id:
                form_id = self.env[res_model].get_request_type_view_id()
                if self._context.get("show_validation_form"):
                    form = (
                        self.env.ref(self.request_type_ref_id.VALIDATION_FORM) or None
                    )
                    if form:
                        form_id = form.id
                action = self.env[res_model].get_formview_action()
                context = {
                    "create": False,
                }
                action.update(
                    {
                        "views": [(form_id, "form")],
                        "res_id": res_id,
                        "target": target,
                        "context": context,
                        "flags": {"mode": mode},
                    }
                )
                return action

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("ERROR!"),
                "message": _("The Request Type field must be filled-up."),
                "sticky": False,
                "type": "danger",
            },
        }

    def open_applicant_form(self, target="current", mode="readonly"):
        self.ensure_one()
        if self.applicant_id:
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

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("ERROR!"),
                "message": _("The Applicant field must be filled-up."),
                "sticky": False,
                "type": "danger",
            },
        }

    def open_user_assignment_wiz(self):
        for rec in self:
            assign_self = False
            if rec.assign_to_id:
                if rec.assign_to_id.id != self.env.user.id:
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
                    "context": {"curr_assign_to_id": rec.assign_to_id.id},
                }
                return action
            else:
                self.assign_to_user(self.env.user)

    def assign_to_user(self, user):
        self.ensure_one()
        user_ok = False
        # Fully validated CRs will proceed
        if self.state in ["draft", "validated", "rejected"]:
            # TODO: User must be a member of administrator and validator HQ
            user_ok = True
        else:
            # Check if user is a member of validators in the validation sequence config
            if self.request_type_ref_id.validation_ids:
                for mrec in self.request_type_ref_id.validation_ids:
                    if mrec.validation_group_id.id in user.groups_id.ids:
                        user_ok = True
                        break
            else:
                raise UserError(
                    _(
                        "This change request does not have any validation sequence defined."
                    )
                )
        if user_ok:
            self.update(
                {
                    "assign_to_id": user.id,
                }
            )
        else:
            raise UserError(
                _(
                    "Only users of groups defined in the validation sequence "
                    "can be assigned to this change request."
                )
            )

    def open_request_detail(self):
        self._check_phone_exist()
        for rec in self:
            # Open Request Form
            return rec.open_change_request_form(target="current", mode="edit")

    # def prepare_directory(self):
    #     """
    #     Prepare the directory for the change request attachments
    #     """
    #     self.ensure_one()
    #     root_dir = self.env["dms.directory"].search(
    #         [("is_root_directory", "=", True), ("name", "=", "Change Requests")]
    #     )
    #     if not root_dir:
    #         res_model = self.request_type
    #         storage = self.env.ref("spp_change_request.dms_change_request_storage")
    #         root_dir = self.env["dms.directory"].create(
    #             {
    #                 "storage_id": storage.id,
    #                 # "res_model": self,
    #                 "group_ids": [(4, storage.field_default_group_id.id)],
    #                 "name": "Change Requests",
    #                 "is_root_directory": True,
    #             }
    #         )
    #     root_dir = root_dir[0]
    #
    #     logging.info("Root Directory: %s", root_dir)
    #
    #     requests_dir = self.env["dms.directory"].search(
    #         [("id", "child_of", root_dir.id), ("name", "=", self.request_type)]
    #     )
    #     if not requests_dir:
    #         res_model = self.request_type
    #         storage = self.env.ref(self.env[res_model].DMS_STORAGE)
    #         requests_dir = self.env["dms.directory"].create(
    #             {
    #                 "name": self.request_type,
    #                 # "storage_id": storage.id,
    #                 "parent_id": root_dir.id,
    #                 # "res_model": self.request_type,
    #                 # "group_ids": [(4, root_dir.group_ids.ids)],
    #                 "is_root_directory": False,
    #             }
    #         )
    #
    #     requests_dir = requests_dir[0]
    #     logging.info("Requests Directory: %s", requests_dir)
    #     return requests_dir
    #
    # def create_folder_for_request(self):
    #     self.ensure_one()
    #     requests_dir = self.prepare_directory()
    #     request_dir = self.env["dms.directory"].search(
    #         [("id", "child_of", requests_dir.id), ("name", "=", self.name)]
    #     )
    #     logging.info("Request Directory before: %s", request_dir)
    #     if not request_dir:
    #         res_model = self.request_type
    #         storage = self.env.ref(self.env[res_model].DMS_STORAGE)
    #         request_dir = self.env["dms.directory"].create(
    #             {
    #                 "name": self.name,
    #                 "storage_id": storage.id,
    #                 "parent_id": requests_dir.id,
    #                 "res_model": self.request_type,
    #                 # "group_ids": [(4, requests_dir.group_ids.ids)],
    #                 "is_root_directory": False,
    #             }
    #         )
    #     logging.info("Request Directory after: %s", request_dir)
    #     request_dir = request_dir[0]
    #
    #     applicant_dir = self.env["dms.directory"].search(
    #         [("id", "child_of", request_dir.id), ("name", "=", "Applicant")]
    #     )
    #     if not applicant_dir:
    #         self.env["dms.directory"].create(
    #             {
    #                 "name": "Applicant",
    #                 "parent_id": request_dir.id,
    #                 "is_root_directory": False,
    #             }
    #         )
    #
    #     return request_dir

    def _check_phone_exist(self):
        if not self.applicant_phone:
            raise UserError(_("Phone No. is required."))

    def create_request_detail(self):
        self._check_phone_exist()

        for rec in self:
            if rec.state in ("draft", "pending"):
                # Set the request_type_ref_id
                res_model = rec.request_type
                # Set the dms directory
                _logger.info(
                    "Change Request: DMS Directory Creation (%s)"
                    % len(self.dms_directory_ids)
                )
                storage = self.env.ref(self.env[res_model].DMS_STORAGE)
                dmsval = {
                    "storage_id": storage.id,
                    # "res_id": rec.id,
                    "res_model": res_model,
                    "is_root_directory": True,
                    "name": rec.name,
                    "group_ids": [(4, storage.field_default_group_id.id)],
                }

                # Prepare CR type model data
                cr_type_vals = {
                    "registrant_id": rec.registrant_id.id,
                    "applicant_id": rec.applicant_id.id,
                    "change_request_id": rec.id,
                    "dms_directory_ids": [(Command.create(dmsval))],
                }

                # Create the change request detail record
                ref_id = self.env[res_model].create(cr_type_vals)
                directory_id = ref_id.dms_directory_ids[0].id

                self.env["dms.directory"].create(
                    {
                        "name": "Applicant",
                        "parent_id": directory_id,
                        "is_root_directory": False,
                    }
                )

                # Upload Scanned IDs to DMS
                dms_file_ids = []
                for id_fld in ["id_document_details", "qr_code_details"]:
                    if rec[id_fld]:
                        dms_id_doc = rec._get_id_doc_vals(directory_id, id_fld)
                        if dms_id_doc:
                            dms_file_ids.append(Command.create(dms_id_doc))
                if dms_file_ids:
                    ref_id.update({"dms_file_ids": dms_file_ids})

                ref_id._onchange_registrant_id()
                request_type_ref_id = f"{res_model},{ref_id.id}"
                _logger.debug("DEBUG! request_type_ref_id: %s", request_type_ref_id)
                rec.update(
                    {
                        "request_type_ref_id": request_type_ref_id,
                        "id_document_details": "",
                    }
                )
                # Open Request Form
                return rec.open_change_request_form(target="current", mode="edit")
            else:
                raise UserError(
                    _(
                        "The change request to be created must be in draft or pending validation state."
                    )
                )

    def _get_id_doc_vals(self, directory_id, id_fld, file_name_prefix: str = ""):
        try:
            details = json.loads(id_fld)
        except json.decoder.JSONDecodeError as e:
            details = None
            _logger.error(e)
        if details and "image" in details:
            return {
                "name": file_name_prefix + details["document_number"] + ".jpg",
                "directory_id": directory_id,
                "content": details["image"],
            }
        return None

    def action_submit(self):
        for rec in self:
            if rec.request_type_ref_id:
                rec.request_type_ref_id._on_submit(rec)
            else:
                raise UserError(
                    _("The change request type must be properly filled-up.")
                )

    def action_validate(self):
        for rec in self:
            return rec.request_type_ref_id._on_validate(rec)

    def action_apply(self):
        for rec in self:
            rec.request_type_ref_id._apply(rec)

    def action_cancel(self):
        """
        This method is called when the Change Request is applied to the live data.

        :raise ValidationError: Exception raised when something is not valid.
        """
        self.ensure_one()

        form_id = self.env.ref("spp_change_request.change_request_cancel_wizard").id
        action = {
            "name": _("Cancel Change Request"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_id": form_id,
            "view_type": "form",
            "res_model": "spp.change.request.cancel.wizard",
            "target": "new",
            "context": {
                "change_request_id": self.id,
            },
        }
        return action

    def _cancel(self, request):
        """
        This method is used to cancel the change request.

        :param request: The request.
        :return:
        """
        self.ensure_one()
        if request.state in ("draft", "pending", "rejected"):
            request.update(
                {
                    "state": "cancelled",
                    "cancelled_by_id": self.env.user.id,
                    "date_cancelled": fields.Datetime.now(),
                    "validator_ids": [(Command.clear())],
                }
            )
            # Mark previous activity as 'done'
            request.last_activity_id.action_done()
        else:
            raise UserError(
                _(
                    "The request to be cancelled must be in draft, pending, or rejected validation state."
                )
            )

    def action_reset_to_draft(self):
        for rec in self:
            rec.request_type_ref_id._reset_to_draft(rec)

    def action_reject(self):
        form_id = self.env.ref("spp_change_request.change_request_reject_wizard").id
        action = {
            "name": _("Reject Change Request"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_id": form_id,
            "view_type": "form",
            "res_model": "spp.change.request.reject.wizard",
            "target": "new",
        }
        return action

    def _check_user(self, process, auto_assign=False):
        self.ensure_one()

        # if no user is assigned, assign to current user
        if not self.assign_to_id and auto_assign:
            self.assign_to_user(self.env.user)

        if self.assign_to_id:
            # Only user assigned to CR is allowed to process
            if self.assign_to_id.id == self.env.user.id:
                return True
            else:
                raise UserError(
                    _("You are not allowed to %s this change request", process)
                )
        else:
            raise UserError(_("There are no user assigned to this change request."))

    @api.depends("validator_ids", "state")
    def _compute_validation_group_id(self):
        for rec in self:
            if rec.state in ["draft", "pending"]:
                validation_stages = None
                validation_stage_ids = None
                if rec.validator_ids:
                    validation_stage_ids = rec.validator_ids.mapped("stage_id.id")

                if rec.request_type_ref_id and rec.request_type_ref_id.validation_ids:
                    if validation_stage_ids:
                        validation_stages = (
                            rec.request_type_ref_id.validation_ids.filtered(
                                lambda a: a.stage_id.id not in validation_stage_ids
                            )
                        )
                    else:
                        validation_stages = rec.request_type_ref_id.validation_ids

                    if validation_stages:
                        stage = validation_stages[0]
                        rec.validation_group_id = stage.validation_group_id

    def _get_validation_stage(self):
        self.ensure_one()
        stage = None
        message = None
        validator_id = self.env.user.id
        # Get the current validators
        validation_stages = None
        validation_stage_ids = None
        if self.validator_ids:
            validation_stage_ids = self.validator_ids.mapped("stage_id.id")
        if self.request_type_ref_id.validation_ids:
            # Get the next validation sequence
            if validation_stage_ids:
                validation_stages = self.request_type_ref_id.validation_ids.filtered(
                    lambda a: a.stage_id.id not in validation_stage_ids
                )
            else:
                validation_stages = self.request_type_ref_id.validation_ids
            if validation_stages:
                if len(validation_stages) == 1:
                    message = "FINAL"
                stage = validation_stages[0]
                # Check if user is allowed to validate request
                if (
                    self.state not in ["draft", "rejected"]
                    and validator_id not in stage.validation_group_id.users.ids
                ):
                    message = _(
                        f"You are not allowed to validate this request! Stage: {stage.stage_id.name}. "
                        f"Allowed Validator Group: {stage.validation_group_id.name}"
                    )
                    stage = None
            else:
                message = _(
                    "Error in validation stages. No available stage to assign to this validation."
                )
        else:
            message = _("There are no validators defined for this request.")
        return stage, message, validator_id

    def _generate_activity(self, activity_type, summary, note):
        self.ensure_one()
        activity_type_id = self.env.ref(activity_type).id
        next_activity = {
            "res_id": self.id,
            "res_model_id": self.env["ir.model"]._get(self._name).id,
            "user_id": self.env.user.id,
            "summary": summary,
            "note": note,
            "activity_type_id": activity_type_id,
            "date_deadline": fields.Date.today(),
        }
        return self.env["mail.activity"].create(next_activity)


class ChangeRequestValidators(models.Model):
    _name = "spp.change.request.validators"
    _description = "Change Request Validators"
    _rec_name = "validator_id"

    request_id = fields.Many2one("spp.change.request", "Change Request")
    stage_id = fields.Many2one(
        "spp.change.request.validation.stage", "Validation Stage", required=True
    )
    validator_id = fields.Many2one("res.users", "Validated by", required=True)
    date_validated = fields.Datetime()


class ChangeRequestValidationSequence(models.Model):
    _name = "spp.change.request.validation.sequence"
    _description = "Change Request Validation Sequence"
    _rec_name = "stage_id"
    _order = "sequence,id"

    sequence = fields.Integer(default=10)
    request_type = fields.Selection(
        selection="_selection_request_type_ref_id", required=True
    )
    stage_id = fields.Many2one(
        "spp.change.request.validation.stage", "Validation Stage", required=True
    )
    validation_group_id = fields.Many2one(
        "res.groups", string="Change Request Validation Group"
    )
    validation_group_state = fields.Selection(
        [
            ("source", "Source Area"),
            ("destination", "Destination Area"),
            ("both", "Apply to Both"),
        ],
        string="Validation Group Application",
        default="both",
        required=True,
    )

    @api.model
    def _selection_request_type_ref_id(self):
        return []
