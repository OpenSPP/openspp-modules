# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import json
import logging

from odoo import _, api, fields, models
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

    _inherit = "spp.change.request"

    # Additional fields specific to this module
    request_type_target = fields.Many2one(
        "spp.change.request.targets", compute="_compute_request_type_target", store=True
    )
    registrant_id_visible = fields.Boolean("Registrant Visible", compute="_compute_registrant_id_visible")
    registrant_id_domain = fields.Binary(
        compute="_compute_registrant_id_domain",
        readonly=True,
        store=False,
    )

    # For ID Scanner Widget
    id_document_details = fields.Text("Scanned ID Document")
    # For QR Code Scanner Widget
    qr_code_details = fields.Text("Scanned QR Card")

    applicant_id = fields.Many2one(
        "res.partner",
        "Applicant",
        domain=[("is_registrant", "=", True), ("is_group", "=", False)],
    )
    applicant_id_required = fields.Boolean("Applicant Required", compute="_compute_applicant_id_required")
    applicant_id_visible = fields.Boolean("Applicant Visible", compute="_compute_applicant_id_visible")
    # Applicant who submitted the change request (In case the registrant is a group, the applicant is the individual)
    applicant_id_domain = fields.Binary(
        compute="_compute_applicant_id_domain",
        readonly=True,
        store=False,
    )
    applicant_phone = fields.Char("Applicant's Phone Number")  #: Applicant's phone number
    applicant_phone_required = fields.Boolean("Applicant's Phone Required", compute="_compute_applicant_phone_required")
    applicant_information_visible = fields.Boolean(
        "Applicant Information Visible", compute="_compute_applicant_information_visible"
    )

    # TODO: @edwin: remove `center` from this variable name
    next_area_center_ids = fields.Many2many(
        "spp.area", string="Next Area"
    )  #: When the change request change the area, we store the destination in case a validation based on it is required

    # Override registrant_id field to add domain
    registrant_id = fields.Many2one(
        "res.partner",
        "Registrant",
        domain=[("is_registrant", "=", True)],
    )  #: Registrant who submitted the change request

    validation_stage = fields.Selection(
        [
            ("local", "Local"),
            ("hq", "HQ"),
            ("completed", "Completed"),
        ],
        string="Validation Stage",
        default="local",
        compute="_compute_validation_stage",
        store=True,
    )

    @api.depends("validator_ids")
    def _compute_validation_stage(self):
        for rec in self:
            validation_sequences = self.env["spp.change.request.validation.sequence"].search(
                [("request_type", "=", rec.request_type)]
            )
            total_sequences = len(validation_sequences)
            total_validators = len(rec.validator_ids)
            if not validation_sequences or total_sequences == 0:
                rec.validation_stage = "local"
            else:
                if total_validators == 0:
                    rec.validation_stage = "local"
                elif total_validators < total_sequences - 1:
                    rec.validation_stage = "local"
                elif total_validators == total_sequences - 1:
                    rec.validation_stage = "hq"
                elif total_validators >= total_sequences:
                    rec.validation_stage = "completed"

    @api.model
    def _registrant_id_not_visible_in_request_type(self):
        return []

    @api.depends("request_type")
    def _compute_registrant_id_visible(self):
        for rec in self:
            rec.registrant_id_visible = (
                bool(rec.request_type) and rec.request_type not in self._registrant_id_not_visible_in_request_type()
            )

    @api.model
    def _applicant_id_not_required_in_request_type(self):
        return []

    @api.model
    def _applicant_id_not_visible_in_request_type(self):
        return []

    @api.depends("request_type")
    def _compute_applicant_id_required(self):
        for rec in self:
            rec.applicant_id_required = rec.request_type not in self._applicant_id_not_required_in_request_type()

    @api.depends("request_type")
    def _compute_applicant_id_visible(self):
        for rec in self:
            rec.applicant_id_visible = (
                bool(rec.request_type) and rec.request_type not in self._applicant_id_not_visible_in_request_type()
            )

    @api.model
    def _applicant_phone_not_required_in_request_type(self):
        return []

    @api.depends("request_type")
    def _compute_applicant_phone_required(self):
        for rec in self:
            rec.applicant_phone_required = rec.request_type not in self._applicant_phone_not_required_in_request_type()

    @api.model
    def _applicant_information_not_visible_in_request_type(self):
        return []

    @api.depends("request_type")
    def _compute_applicant_information_visible(self):
        for rec in self:
            rec.applicant_information_visible = (
                bool(rec.request_type)
                and rec.request_type not in self._applicant_information_not_visible_in_request_type()
            )

    @api.onchange("request_type")
    def _onchange_request_type(self):
        self._compute_request_type_target()
        self.registrant_id = None

    @api.depends("request_type")
    def _compute_request_type_target(self):
        for rec in self:
            request_type_target = None
            if rec.request_type:
                request_type_targets = self.env["spp.change.request.targets"].search(
                    [("name", "=", rec.request_type)], limit=1
                )
                if request_type_targets:
                    request_type_target = request_type_targets.id

            rec.request_type_target = request_type_target

    @api.depends("request_type_target")
    def _compute_registrant_id_domain(self):
        """
        Called whenever request_type_target field is changed

        This method is used for dynamic domain of registrant_id field
        """
        for rec in self:
            domain = [("id", "=", 0)]
            if rec.request_type_target:
                if rec.request_type_target.target == "individual":
                    domain = [("is_registrant", "=", True), ("is_group", "=", False)]
                elif rec.request_type_target.target == "group":
                    domain = [("is_registrant", "=", True), ("is_group", "=", True)]
                else:
                    domain = [("is_registrant", "=", True)]

            rec.registrant_id_domain = domain

    @api.depends("registrant_id")
    def _compute_applicant_id_domain(self):
        """
        Called whenever registrant_id field is changed

        This method is used for dynamic domain of applicant_id field
        """
        for rec in self:
            domain = [("id", "=", 0)]
            if rec.registrant_id:
                if rec.registrant_id.is_group:
                    # TODO: Use the is_ended field to filter
                    # Get only the members with non-expired membership
                    group_memberships = rec.registrant_id.group_membership_ids.filtered(
                        lambda a: not a.ended_date or a.ended_date > fields.Datetime.now()
                    )
                    if group_memberships:
                        group_membership_ids = group_memberships.mapped("individual.id")
                        domain = [("id", "in", group_membership_ids)]
                else:
                    domain = [("is_registrant", "=", True), ("is_group", "=", False)]

            rec.applicant_id_domain = domain

    @api.onchange("registrant_id")
    def _onchange_registrant_id(self):
        """
        Called whenever registrant_id field is changed

        Remove applicant_id field's value and applicant_phone field's value in the UI
        whenever the user is selecting values in registrant_id field

        :param:

        :return:

        :raise:
        """

        if self.registrant_id:
            self.update(
                {
                    "applicant_id": None,
                    "applicant_phone": None,
                }
            )

    @api.onchange("applicant_id")
    def _onchange_applicant_id(self):
        """
        Called whenever applicant_id field is changed

        This method updates the applicant_phone field based on phone field of applicant_id

        :param:

        :return:

        :raise:
        """
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
        """
        Called whenever registrant_id and applicant_phone field are saved

        This method checks the format of applicant_phone

        :param:

        :return:

        :raise ValidationError: Exception raised when phone number format is not valid.
        """
        for rec in self:
            country_code = (
                rec.registrant_id.country_id.code
                if rec.registrant_id and rec.registrant_id.country_id and rec.registrant_id.country_id.code
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
        """
        This method is called whenever there is a change in the value of id_document_details field.

        Updates other fields based on the field value of id_document_details

        id_document_details must be a JSON Serializable

        NOTE: Must be used in conjunction with an ID document scanner.
            : e.g. passport scanner, qr code scanner

        :return:

        :raise UserError: Exception raised when something is not valid.
        """
        if self.id_document_details:
            try:
                details = json.loads(self.id_document_details)
            except json.decoder.JSONDecodeError as e:
                details = None
                _logger.error(e)
            if details:
                if self.registrant_id:
                    group_membership_ids = self.registrant_id.group_membership_ids.mapped("individual.id")
                    domain = [
                        ("partner_id", "in", group_membership_ids),
                        ("value", "=", details.get("document_number", "").strip()),
                    ]
                    id_docs = self.env["g2p.reg.id"].search(domain)
                    if id_docs:
                        vals = {
                            "applicant_id": id_docs[0].partner_id.id,
                            "applicant_phone": id_docs[0].partner_id.phone,
                        }
                        self.update(vals)
                    else:
                        raise UserError(_("There are no registrant found with the ID number scanned."))
                else:
                    raise UserError(_("A group must be selected."))
            else:
                raise UserError(_("There are no data captured from the ID scanner."))

    @api.onchange("qr_code_details")
    def _onchange_scan_qr_code_details(self):
        """
        This method is called whenever there is a change in the value of qr_code_details field.

        Updates other fields based on the field value of qr_code_details

        qr_code_details must be a JSON Serializable

        NOTE: Must be used in conjunction with an ID document scanner.
            : e.g. passport scanner, qr code scanner

        :return:

        :raise UserError: Exception raised when something is not valid.
        """
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
                    raise UserError(_("There are no group found with the ID number from the QR Code scanned."))
            else:
                raise UserError(_("There are no data captured from the QR Code scanner."))

    def open_applicant_form(self, target="current", mode="readonly"):
        """
        Get and opens the form view of the applicant_id to view details

        Returns an error display notification when no applicant is selected.

        Usage:
        - Add this function in the name of button with type object in XML

        example:
            <button
                name="open_applicant_form"
                type="object"
            />

        NOTE: To change the values of a parameter and use it to xml, I suggest you to create a new function and
              call this function with different arguments

        example:
            def new_open_request_form(self):
                return self.open_applicant_form(target="<other_value>", mode="<other_value>")

            <button
                name="new_open_request_form"
                type="object"
            />

        :param str target:
        :param str readonly:

        :return dict action: form view action

        :raise:
        """
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

    def open_request_detail(self):
        """
        Validate Phone then Opens the form view of the selected request type

        :return dict action: form view action

        :raise UserError: Exception raised when applicant_phone is not existing.
        """

        self._check_phone_exist()
        for rec in self:
            # Open Request Form
            mode = "edit"
            if self.env.user.id not in [self.assign_to_id.id, self.create_uid.id]:
                mode = "readonly"
            return rec.open_change_request_form(target="current", mode=mode)

    def _check_phone_exist(self):
        """
        Checks if phone is existing

        :raise UserError: Exception raised when applicant_phone is not existing.
        """
        if not self.applicant_phone and self.applicant_phone_required:
            raise UserError(_("Phone No. is required."))

    def create_request_detail_no_redirect(self):
        """
        Creates the request_type_ref record

        Usage:
        - Add this function in the name of button with type object in XML

        example:
            <button
                name="create_request_detail_no_redirect"
                type="object"
            />

        NOTE: do not return the action of create_request_detail to not do redirection of page

        :return dict action: form view action

        :raise UserError: Exception raised when applicant_phone is not existing.
        """

        # Called the function without return
        self.create_request_detail()

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

    def approve_cr(self):
        """
        Approve the change request when the user is allowed to directly apply the changes.

        Usage:
        - Call this function via XMLRPC
        :raise ValidationError: Exception raised when user is allowed to directly approve the CR.
        """
        self.ensure_one()
        # Check if user is allowed to directly approve the CR
        if not self.env.user.has_group("spp_change_request.group_spp_change_request_external_api"):
            raise ValidationError(_("User is not allowed to approve CRs directly."))
        return self.request_type_ref_id._approve_cr(self)

    # Override the action_cancel method to use the correct wizard reference
    def action_cancel(self):
        """
        Get and opens the wizard form change_request_cancel_wizard to cancel the change request

        Usage:
        - Add this function in the name of button with type object in XML

        example:
            <button
                name="action_cancel"
                type="object"
            />

        :raise ValidationError: Exception raised when something is not valid.
        """
        self.ensure_one()

        form_id = self.env.ref("spp_change_request_base.change_request_cancel_wizard").id
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

    # Override the action_reject method to use the correct wizard reference
    def action_reject(self):
        """
        Opens reject wizard form change_request_reject_wizard

        Usage:
        - Add this function in the name of button with type object in XML

        example:
            <button
                name="action_reset_to_draft"
                type="object"
            />

        :param:

        :return: action
        :rtype: dict
        """

        form_id = self.env.ref("spp_change_request_base.change_request_reject_wizard").id
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
