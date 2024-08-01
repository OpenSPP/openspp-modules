import json
import logging

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from odoo.addons.phone_validation.tools import phone_validation

_logger = logging.getLogger(__name__)


class ChangeRequestTypeCustomChangeInfo(models.Model):
    _inherit = "spp.change.request"

    registrant_id = fields.Many2one(
        "res.partner",
        "Registrant",
        domain=[("is_registrant", "=", True), ("is_group", "=", False)],
    )

    @api.model
    def _selection_request_type_ref_id(self):
        selection = super()._selection_request_type_ref_id()
        new_request_type = ("spp.change.request.change.info", "Change Information")
        if new_request_type not in selection:
            selection.append(new_request_type)
        return selection


class ChangeRequestAddChildren(models.Model):
    _name = "spp.change.request.change.info"
    _inherit = [
        "spp.change.request.source.mixin",
        "spp.change.request.validation.sequence.mixin",
    ]
    _description = "Change Information Change Request Type"
    _order = "id desc"

    # Initialize CR constants
    VALIDATION_FORM = "spp_change_request_change_info.view_change_request_change_info_validation_form"
    REQUIRED_DOCUMENT_TYPE = [
        "spp_change_request_change_info.spp_dms_change_info",
        # "spp_change_request.spp_dms_birth_certificate",
        # "spp_change_request.spp_dms_applicant_spp_card",
        # "spp_change_request.spp_dms_applicant_uid_card",
        # "spp_change_request.spp_dms_custody_certificate",
    ]

    # Mandatory initialize source and destination center areas
    # If validators will be allowed for both, make the values the same
    SRC_AREA_FLD = ["registrant_id", "area_center_id"]
    DST_AREA_FLD = SRC_AREA_FLD

    def _get_dynamic_selection(self):
        options = self.env["gender.type"].search([])
        return [(option.value, option.code) for option in options]

    # Redefine registrant_id to set specific domain and label
    registrant_id = fields.Many2one(
        "res.partner",
        "Add to Group",
        domain=[("is_registrant", "=", True), ("is_group", "=", False)],
    )

    request_type = fields.Selection(related="change_request_id.request_type")

    # For ID Scanner Widget
    id_document_details = fields.Text("ID Document")

    # Change Request Fields
    full_name = fields.Char(compute="_compute_full_name", readonly=True)
    family_name = fields.Char()
    given_name = fields.Char()
    addl_name = fields.Char("Additional Name")

    birth_place = fields.Char()
    birthdate_not_exact = fields.Boolean()
    birthdate = fields.Date("Date of Birth")
    gender = fields.Selection(selection=_get_dynamic_selection)
    phone = fields.Char("Phone Number")
    national_id_number = fields.Char("National ID Number")

    # Farmer Details
    image_1920 = fields.Binary()
    highest_education_level = fields.Selection(
        [
            ("none", "None"),
            ("primary", "Primary"),
            ("secondary", "Secondary"),
            ("tertiary", "Tertiary"),
        ],
        string="Highest Educational Level",
    )

    applicant_relation = fields.Selection(
        [("father", "Father"), ("mother", "Mother"), ("grandfather", "Grandfather")],
        "Relationship to Applicant",
    )

    # Add domain to inherited field: validation_ids
    validation_ids = fields.Many2many(
        relation="spp_change_request_change_info_rel",
        domain=[("request_type", "=", _name)],
    )

    # DMS Field
    dms_directory_ids = fields.One2many(
        "spp.dms.directory",
        "change_request_change_info_id",
        string="DMS Directories",
        auto_join=True,
    )
    dms_file_ids = fields.One2many(
        "spp.dms.file",
        "change_request_change_info_id",
        string="DMS Files",
        auto_join=True,
    )

    @api.onchange("birthdate")
    def _onchange_birthdate(self):
        if self.birthdate and self.birthdate > fields.date.today():
            raise ValidationError(_("Birthdate should not be on a later date."))

    @api.constrains("national_id_number")
    def _check_national_id_number(self):
        for rec in self:
            if rec.national_id_number and len(rec.national_id_number) > 0:
                if len(rec.national_id_number) != 12:
                    raise ValidationError(_("National ID Number must be 12 digits long."))

    @api.constrains("phone")
    def _check_phone(self):
        for rec in self:
            cr = rec.change_request_id
            country_code = (
                cr.registrant_id.country_id.code
                if cr.registrant_id and cr.registrant_id.country_id and cr.registrant_id.country_id.code
                else None
            )
            if country_code is None:
                country_code = (
                    cr.company_id.country_id.code
                    if cr.company_id.country_id and cr.company_id.country_id.code
                    else None
                )
            try:
                phone_validation.phone_parse(rec.phone, country_code)
            except UserError as e:
                raise ValidationError(_("Incorrect phone number format")) from e

    @api.depends("given_name", "addl_name", "family_name")
    def _compute_full_name(self):
        for rec in self:
            full_name = f"{rec.family_name or ''}, {rec.given_name or ''}" f" {rec.addl_name or ''}"
            rec.full_name = full_name.title()

    @api.onchange("registrant_id")
    def _onchange_registrant_id(self):
        pass

    @api.onchange("id_document_details")
    def _onchange_scan_id_document_details(self):
        if self.dms_directory_ids:
            if self.id_document_details:
                try:
                    details = json.loads(self.id_document_details)
                except json.decoder.JSONDecodeError as e:
                    details = None
                    _logger.error(e)
                if details:
                    # Upload to DMS
                    if details["image"]:
                        if self._origin:
                            directory_id = self._origin.dms_directory_ids[0].id
                        else:
                            directory_id = self.dms_directory_ids[0].id
                        dms_vals = {
                            "name": "UID_" + details["document_number"] + ".jpg",
                            "directory_id": directory_id,
                            "category_id": self.env.ref("spp_change_request.spp_dms_uid_card").id,
                            "content": details["image"],
                        }
                        # TODO: Should be added to vals["dms_file_ids"] but it is
                        # not writing to one2many field using Command.create()
                        self.env["spp.dms.file"].create(dms_vals)

                    # TODO: grand_father_name and father_name
                    vals = {
                        "family_name": details["family_name"],
                        "given_name": details["given_name"],
                        "birthdate": details["birth_date"],
                        "gender": details["gender"],
                        "id_document_details": "",
                        "birth_place": details["birth_place_city"],
                        # TODO: Fix not writing to one2many field: dms_file_ids
                        # "dms_file_ids": [(Command.create(dms_vals))],
                    }
                    self.update(vals)
        else:
            raise UserError(_("There are no directories defined for this change request."))

    def _get_default_change_request_id(self):
        """
        Get the default field name for change request id.
        """
        return "default_change_request_change_info_id"

    def validate_data(self):
        if not self.given_name:
            raise ValidationError("Given Name is required!")
        if not self.family_name:
            raise ValidationError("Family Name is required!")
        super().validate_data()
        return

    def update_live_data(self):
        self.ensure_one()
        # Create a new individual (res.partner)
        if self.phone:
            phone_rec = [
                Command.create(
                    {
                        "phone_no": self.phone,
                    }
                )
            ]
        else:
            phone_rec = None
        if self.national_id_number:
            nid_rec = [
                Command.create(
                    {
                        "id_type": self.env.ref("spp_change_request_change_info.national_id_type").id,
                        "value": self.national_id_number,
                    }
                )
            ]
        else:
            nid_rec = None
        vals = {}
        if self.full_name:
            vals.update({"name": self.full_name})
        if self.family_name:
            vals.update({"family_name": self.family_name})
        if self.given_name:
            vals.update({"given_name": self.given_name})
        if self.addl_name:
            vals.update({"addl_name": self.addl_name})
        if self.birth_place:
            vals.update({"birth_place": self.birth_place})
        if self.birthdate_not_exact:
            vals.update({"birthdate_not_exact": self.birthdate_not_exact})
        if self.birthdate:
            vals.update({"birthdate": self.birthdate})
        if self.gender:
            vals.update({"gender": self.gender})
        if self.image_1920:
            vals.update({"image_1920": self.image_1920})
        if self.highest_education_level:
            vals.update({"highest_education_level": self.highest_education_level})
        if phone_rec:
            vals.update({"phone_number_ids": phone_rec})
        if nid_rec:
            vals.update({"reg_ids": nid_rec})
        # Updating Registrant
        self.registrant_id.sudo().write(vals)

    def open_registrant_details_form(self):
        self.ensure_one()
        res_id = self.registrant_id.id
        form_id = self.env.ref("g2p_registry_individual.view_individuals_form").id
        action = self.env["res.partner"].get_formview_action()
        context = {
            "create": False,
            "edit": False,
            "hide_from_cr": 1,
        }
        action.update(
            {
                "name": _("Registrant Details"),
                "views": [(form_id, "form")],
                "res_id": res_id,
                "target": "new",
                "context": context,
                "flags": {"mode": "readonly"},
            }
        )
        return action
