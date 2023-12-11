import json
import logging

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from odoo.addons.phone_validation.tools import phone_validation

_logger = logging.getLogger(__name__)


class ChangeRequestTypeCustomAddChildren(models.Model):
    _inherit = "spp.change.request"

    registrant_id = fields.Many2one(
        "res.partner",
        "Registrant",
        domain=[("is_registrant", "=", True), ("is_group", "=", True)],
    )

    @api.model
    def _selection_request_type_ref_id(self):
        selection = super()._selection_request_type_ref_id()
        new_request_type = ("spp.change.request.add.children", "Add Child/Member")
        if new_request_type not in selection:
            selection.append(new_request_type)
        return selection


class ChangeRequestAddChildren(models.Model):
    _name = "spp.change.request.add.children"
    _inherit = [
        "spp.change.request.source.mixin",
        "spp.change.request.validation.sequence.mixin",
    ]
    _description = "Add Child/Member Change Request Type"
    _order = "id desc"

    # Initialize DMS Storage
    DMS_STORAGE = "spp_change_request_add_children_demo.attachment_storage_add_children"
    VALIDATION_FORM = "spp_change_request_add_children_demo.view_change_request_add_children_validation_form"
    REQUIRED_DOCUMENT_TYPE = [
        # "spp_change_request_add_children_demo.spp_dms_add_children",
        "spp_change_request_add_children_demo.spp_dms_birth_certificate",
        # "spp_change_request_add_children_demo.spp_dms_applicant_spp_card",
        # "spp_change_request_add_children_demo.spp_dms_applicant_uid_card",
        # "spp_change_request_add_children_demo.spp_dms_custody_certificate",
    ]

    # Mandatory initialize source and destination center areas
    # If validators will be allowed for both, make the values the same
    SRC_AREA_FLD = ["registrant_id", "area_center_id"]
    DST_AREA_FLD = SRC_AREA_FLD

    # Redefine registrant_id to set specific domain and label
    registrant_id = fields.Many2one(
        "res.partner",
        "Add to Group",
        domain=[("is_registrant", "=", True), ("is_group", "=", True)],
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
    gender = fields.Selection(
        [("Female", "Female"), ("Male", "Male")],
    )
    phone = fields.Char("Phone Number")
    uid_number = fields.Char("UID Number")

    kind = fields.Many2many(
        "g2p.group.membership.kind", string="Group Membership Types"
    )

    applicant_relation = fields.Selection(
        [("father", "Father"), ("mother", "Mother"), ("grandfather", "Grandfather")],
        "Relationship to Applicant",
    )

    # Target Group Fields
    group_member_ids = fields.One2many(
        "spp.change.request.group.members", "group_add_children_id", "Group Members"
    )

    # Add domain to inherited field: validation_ids
    validation_ids = fields.Many2many(
        relation="spp_change_request_add_children_demo_rel",
        domain=[("request_type", "=", _name)],
    )

    @api.onchange("birthdate")
    def _onchange_birthdate(self):
        if self.birthdate and self.birthdate > fields.date.today():
            raise ValidationError(_("Birthdate should not be on a later date."))

    @api.onchange("registrant_id")
    def _onchange_registrant_id(self):
        if self.group_member_ids:
            self.group_member_ids = [(Command.clear())]
        # Populate the group members
        self._copy_group_member_ids("group_add_children_id")

    @api.constrains("uid_number")
    def _check_unified_id(self):
        for rec in self:
            if rec.uid_number and len(rec.uid_number) > 0:
                if len(rec.uid_number) != 12:
                    raise ValidationError(_("UID Number must be 12 digits long."))

    @api.constrains("phone")
    def _check_phone(self):
        for rec in self:
            cr = rec.change_request_id
            country_code = (
                cr.registrant_id.country_id.code
                if cr.registrant_id
                and cr.registrant_id.country_id
                and cr.registrant_id.country_id.code
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
            full_name = (
                f"{rec.family_name or ''}, {rec.given_name or ''}"
                f" {rec.addl_name or ''}"
            )
            rec.full_name = full_name.title()

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
                            "category_id": self.env.ref(
                                "spp_change_request.spp_dms_uid_card"
                            ).id,
                            "content": details["image"],
                        }
                        # TODO: Should be added to vals["dms_file_ids"] but it is
                        # not writing to one2many field using Command.create()
                        self.env["dms.file"].create(dms_vals)

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
            raise UserError(
                _("There are no directories defined for this change request.")
            )

    def validate_data(self):
        super().validate_data()
        if not self.family_name:
            raise ValidationError(_("The Family Name is required."))
        if not self.given_name:
            raise ValidationError(_("The First Name is required."))
        if not self.birthdate:
            raise ValidationError(_("The Date of Birth is required."))
        if not self.applicant_relation:
            raise ValidationError(_("The Relationship to Applicant is required."))
        if not self.gender:
            raise ValidationError(_("The Gender is required."))
        # If mother or father, make the custody certificate required
        # if self.applicant_relation in ("mother", "grandfather"):
        #     custody_docs = self.env["dms.file"].search(
        #         [
        #             (
        #                 "category_id",
        #                 "=",
        #                 self.env.ref(
        #                     "spp_change_request_add_children_demo.spp_dms_custody_certificate"
        #                 ).id,
        #             ),
        #             ("res_id", "=", self.id),
        #         ]
        #     )
        #     if not custody_docs:
        #         raise ValidationError(_("The Custody Certificate is required."))

        return

    def update_live_data(self):
        self.ensure_one()
        # Create a new individual (res.partner)
        kinds = []
        for rec in self.kind:
            kinds.append(Command.link(rec.id))
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
        if self.uid_number:
            uid_rec = [
                Command.create(
                    {
                        "id_type": self.env.ref(
                            "spp_change_request_add_children_demo.unified_id_type"
                        ).id,
                        "value": self.uid_number,
                    }
                )
            ]
        else:
            uid_rec = None
        individual_id = self.env["res.partner"].create(
            {
                "is_registrant": True,
                "is_group": False,
                "name": self.full_name,
                "family_name": self.family_name,
                "given_name": self.given_name,
                "addl_name": self.addl_name,
                "birth_place": self.birth_place,
                "birthdate_not_exact": self.birthdate_not_exact,
                "birthdate": self.birthdate,
                "gender": self.gender,
                "phone_number_ids": phone_rec,
                "reg_ids": uid_rec,
            }
        )
        individual_id.phone_number_ids_change()
        # Add to group
        self.env["g2p.group.membership"].create(
            {
                "group": self.registrant_id.id,
                "individual": individual_id.id,
                "kind": kinds,
            }
        )

    def open_registrant_details_form(self):
        self.ensure_one()
        res_id = self.registrant_id.id
        form_id = self.env.ref("g2p_registry_group.view_groups_form").id
        action = self.env["res.partner"].get_formview_action()
        context = {
            "create": False,
            "edit": False,
            "hide_from_cr": 1,
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
