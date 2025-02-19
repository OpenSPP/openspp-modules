# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import json
import logging

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from odoo.addons.phone_validation.tools import phone_validation

_logger = logging.getLogger(__name__)


class ChangeRequestBase(models.Model):
    _inherit = "spp.change.request"

    APPLICANT_FORM_ID = ""
    ADMIN_GROUP_NAME = "spp_change_request.group_spp_change_request_administrator"

    request_type_target = fields.Many2one(
        "spp.change.request.targets", compute="_compute_request_type_target", store=True
    )
    registrant_id = fields.Many2one(
        "res.partner",
        "Registrant",
        domain=[("is_registrant", "=", True)],
    )  #: Registrant who submitted the change request
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
    # Applicant who submitted the change request (In case the registrant is a group, the applicant is the individual)
    applicant_id_domain = fields.Binary(
        compute="_compute_applicant_id_domain",
        readonly=True,
        store=False,
    )
    applicant_phone = fields.Char("Applicant's Phone Number")  #: Applicant's phone number

    next_area_center_ids = fields.Many2many(
        "spp.area", string="Next Area"
    )  #: When the change request change the area, we store the destination in case a validation based on it is required

    @api.onchange("request_type")
    def _onchange_request_type(self):
        """
        Called whenever request_type field is changed
        Get the request_type_target and clear the registrant_id field.
        """
        self._compute_request_type_target()
        self.registrant_id = None

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
            if self.env.user.id not in [self.assign_to_id.id, self.create_uid]:
                mode = "readonly"
            return rec.open_change_request_form(target="current", mode=mode)

    def _check_phone_exist(self):
        """
        Checks if phone is existing

        :raise UserError: Exception raised when applicant_phone is not existing.
        """
        if not self.applicant_phone:
            raise UserError(_("Phone No. is required."))

    def create_request_detail(self):
        """
        Creates the request_type_ref record then opens the form view of the selected request type

        Usage:
        - Add this function in the name of button with type object in XML

        example:
            <button
                name="create_request_detail"
                type="object"
            />

        :return dict action: form view action

        :raise UserError: Exception raised when applicant_phone is not existing.
        """
        self._check_phone_exist()

        for rec in self:
            if rec.state in ("draft", "pending"):
                # Set the request_type_ref_id
                res_model = rec.request_type
                # Set the dms directory
                _logger.debug("Change Request: DMS Directory Creation (%s)" % len(rec.dms_directory_ids))
                dmsval = {
                    "is_root_directory": True,
                    "name": rec.name,
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

                self.env["spp.dms.directory"].create(
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
                raise UserError(_("The change request to be created must be in draft or pending validation state."))

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
