import json
import logging

from dateutil.relativedelta import relativedelta

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from odoo.addons.phone_validation.tools import phone_validation

_logger = logging.getLogger(__name__)


class ChangeRequestTypeCustomAddChildMember(models.Model):
    _inherit = "spp.change.request"

    @api.model
    def _selection_request_type_ref_id(self):
        selection = super()._selection_request_type_ref_id()
        new_request_type = (
            "spp.change.request.add.child",
            "Add Child/Member",
        )
        if new_request_type not in selection:
            selection.append(new_request_type)
        return selection


class ChangeRequestAddChildMember(models.Model):
    _name = "spp.change.request.add.child"
    _inherit = [
        "spp.change.request.source.mixin",
        "spp.change.request.validation.sequence.mixin",
    ]
    _description = "Add Child/Member Change Request Type"
    _order = "id desc"

    # Initialize DMS Storage
    DMS_STORAGE = "spp_change_request_add_child.attachment_storage_add_child"
    VALIDATION_FORM = (
        "spp_change_request_add_child.view_change_request_add_child_validation_form"
    )
    REQUIRED_DOCUMENT_TYPE = []

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
    given_name = fields.Char("First Name")
    father_name = fields.Char("Father's Name")
    grand_father_name = fields.Char("Grand Father's Name")
    family_name = fields.Char("Last Name")

    birth_place = fields.Char()
    birthdate_not_exact = fields.Boolean()
    birthdate = fields.Date("Date of Birth")
    age = fields.Char(compute="_compute_calc_age", size=50, readonly=True, store=True)
    gender = fields.Selection(
        [("Female", "Female"), ("Male", "Male")],
    )
    phone = fields.Char("Phone Number")

    kind = fields.Many2many(
        "g2p.group.membership.kind", string="Group Membership Types"
    )

    applicant_relation = fields.Selection(
        [("father", "Father"), ("mother", "Mother"), ("grandfather", "Grandfather")],
        "Applicant's relation to Child/Member",
    )

    # Target Group Fields
    group_member_ids = fields.One2many(
        "spp.change.request.group.members", "group_add_child_id", "Group Members"
    )

    # Add domain to inherited field: validation_ids
    validation_ids = fields.Many2many(
        relation="spp_change_request_add_child_rel",
        domain=[("request_type", "=", _name)],
    )
    child_ids = fields.One2many(
        comodel_name="spp.change.request.add.member.child",
        inverse_name="parent_id",
        string="Members to Add",
        auto_join=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    source = fields.Selection(
        selection=[
            ("pds", "pds"),
            ("api_tamwini", "api_tamwini"),
        ],
        string="Created Source",
        default="pds",
        readonly=True,
    )

    def api_insert_details(self, vals):
        for rec in self:
            if vals.request_details:
                request_details = vals.request_details[0]
                if request_details.add_member:
                    for cr_details in request_details.add_member:
                        cr_vals = {
                            "given_name": cr_details.given_name or None,
                            "father_name": cr_details.father_name or None,
                            "grand_father_name": cr_details.grand_father_name or None,
                            "family_name": cr_details.family_name or None,
                            "gender": cr_details.gender or None,
                            "phone": cr_details.phone or None,
                            "uid_number": cr_details.uid_number or None,
                            "birth_place": cr_details.birth_place or None,
                            "birthdate_not_exact": cr_details.birthdate_not_exact
                            or False,
                            "birthdate": cr_details.birthdate or None,
                            "applicant_relation": cr_details.applicant_relation or None,
                            "source": "api_tamwini",
                        }

                        rec.update(cr_vals)

                        if cr_details.documents:
                            rec._get_documents_from_api(cr_details.documents)

                    rec.action_submit()

    @api.depends("birthdate")
    def _compute_calc_age(self):
        for line in self:
            line.age = self.compute_age_from_dates(line.birthdate)

    def compute_age_from_dates(self, partner_dob):
        now = fields.Date.today()
        if partner_dob:
            dob = partner_dob
            delta = relativedelta(now, dob)
            # years_months_days = str(delta.years) +"y "+ str(delta.months) +"m "+ str(delta.days)+"d"
            years_months_days = str(delta.years)
        else:
            years_months_days = "No Birthdate!"
        return years_months_days

    @api.onchange("birthdate")
    def _onchange_birthdate(self):
        """
        Called whenever birthdate field is changed

        Checks if the selected birthdate is less than or equal to the current date

        :raise ValidationError: Exception raised when birthdate is greater than the current date.
        """
        if self.birthdate and self.birthdate > fields.date.today():
            raise ValidationError(_("Birthdate should not be on a later date."))

    @api.onchange("registrant_id")
    def _onchange_registrant_id(self):
        """
        Called whenever registrant_id field is changed

        Clears the values of group_member_ids and copy the group members of the registrant

        :param:

        :return:

        :raise:
        """
        if self.group_member_ids:
            self.group_member_ids = [(Command.clear())]
        # Populate the group members
        self._copy_group_member_ids("group_add_child_id")

    @api.constrains("phone")
    def _check_phone(self):
        """
        Called whenever phone field is saved

        Checks the format of phone field

        :raise ValidationError: Exception raised when invalid phone number format.
        """
        for rec in self:
            if rec.phone:
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

    @api.depends("given_name", "father_name", "grand_father_name", "family_name")
    def _compute_full_name(self):
        """
        Called whenever there are changes in any of the following fields:
        given_name
        father_name
        grand_father_name
        family_name

        Combines given_name, father_name, grand_father_name, and family_name and saved to
        full_name field
        """
        for rec in self:
            full_name = (
                f"{rec.given_name or ''} {rec.father_name or ''}"
                f" {rec.grand_father_name or ''} {rec.family_name or ''}"
            )
            rec.full_name = full_name.title()

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
        if self.dms_directory_ids:
            if self.id_document_details:
                try:
                    details = json.loads(self.id_document_details)
                except json.decoder.JSONDecodeError as e:
                    details = None
                    _logger.error(e)
                if details:
                    vals = {
                        "family_name": details.get("family_name", None),
                        "given_name": details.get("given_name", None),
                        "birthdate": details.get("birth_date", None),
                        "uid_number": details.get("document_number", None),
                        "father_name": details.get("father_name", None),
                        "grand_father_name": details.get("grand_father_name", None),
                        "gender": details.get("gender", None),
                        "id_document_details": "",
                        "birth_place": details.get("birth_place_city", None),
                    }

                    # Upload to DMS
                    if details.get("image") and details.get("document_number"):
                        if self._origin:
                            directory_id = self._origin.dms_directory_ids[0].id
                        else:
                            directory_id = self.dms_directory_ids[0].id
                        name = f"UID_{details['document_number']}.jpg"

                        # Check if dms file with specific name is already existing in the directory_id
                        search_dms_file = self.env["dms.file"].search(
                            [("name", "=", name), ("directory_id", "=", directory_id)]
                        )
                        if search_dms_file:
                            # if existing, update the content
                            for dms in search_dms_file:
                                dms.update({"content": details["image"]})
                        else:
                            # if not existing, create a new dms file
                            dms_vals = {
                                "name": name,
                                "directory_id": directory_id,
                                "category_id": self.env.ref(
                                    "pds_change_request.pds_dms_uid_card"
                                ).id,
                                "content": details["image"],
                            }
                            dms_file_id = self.env["dms.file"].create(dms_vals)
                            vals.update({"dms_file_ids": [(4, dms_file_id.id)]})

                    self.update(vals)
        else:
            raise UserError(
                _("There are no directories defined for this change request.")
            )

    def action_submit(self):
        for rec in self:
            rec._copy_from_childs()
        return super().action_submit()

    def _copy_from_childs(self):
        self.ensure_one()
        if not self.child_ids:
            return
        to_copy = self.child_ids[0]
        return self.write(
            {
                "given_name": to_copy.given_name,
                "father_name": to_copy.father_name,
                "grand_father_name": to_copy.grand_father_name,
                "family_name": to_copy.family_name,
                "birth_place": to_copy.birth_place,
                "birthdate": to_copy.birthdate,
                "gender": to_copy.gender,
                "phone": to_copy.phone,
                "kind": [(6, 0, to_copy.kind.ids)],
                "applicant_relation": to_copy.applicant_relation,
            }
        )

    def validate_data(self):
        """
        Override validate_data method

        Add additional validations, compile errors if there's any, and display the
        error message/s in the UI.

        :return:
        """
        super().validate_data()

        error_messages = []

        if not self.given_name:
            error_messages.append(_("The First Name is required."))
        if not self.father_name:
            error_messages.append(_("The Father Name is required."))
        if not self.grand_father_name:
            error_messages.append(_("The Grand Father Name is required."))
        if not self.birthdate:
            error_messages.append(_("The Date of Birth is required."))
        if self.age.isdigit():
            age = int(self.age)
            if age < 18 and not self.applicant_relation:
                error_messages.append(
                    _("The Applicant's relation to Child is required.")
                )
        if not self.gender:
            error_messages.append(_("The Gender is required."))

        if error_messages:
            raise ValidationError("\n".join(error_messages))
        return

    def update_live_data_from_childs(self):
        self.ensure_one()
        for member_to_add in self.child_ids:
            member_to_add._create_new_individual()

    def update_live_data(self):
        """
        Update data when the change request is already validated by all validators
        and change request's state is applied

        :return:

        :raise:
        """
        self.ensure_one()
        if self.child_ids:
            return self.update_live_data_from_childs()
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

        individual_id = self.env["res.partner"].create(
            {
                "is_registrant": True,
                "is_group": False,
                "name": self.full_name,
                "given_name": self.given_name,
                "father_name": self.father_name,
                "grand_father_name": self.grand_father_name,
                "family_name": self.family_name,
                "birth_place": self.birth_place,
                "birthdate_not_exact": self.birthdate_not_exact,
                "birthdate": self.birthdate,
                "gender": self.gender,
                "phone_number_ids": phone_rec,
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
        """
        Opens a modal form that consists of registrant's details

        NOTE: use update when you want to change or add key-value on action

        example:
            action.update({'key': 'value'})

        Check other change request module's open_registrant_details_form for reference

        :return dict action: form view action

        :raise:
        """
        action = super().open_registrant_details_form()

        return action
