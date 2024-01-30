import logging

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from odoo.addons.phone_validation.tools import phone_validation

_logger = logging.getLogger(__name__)


class ChangeRequestTypeCustomAddGroup(models.Model):
    _inherit = "spp.change.request"

    @api.model
    def _selection_request_type_ref_id(self):
        selection = super()._selection_request_type_ref_id()
        new_request_type = ("spp.change.request.add.group", "Add Group")
        if new_request_type not in selection:
            selection.append(new_request_type)
        return selection


class ChangeRequestAddGroup(models.Model):
    _name = "spp.change.request.add.group"
    _inherit = [
        "spp.change.request.source.mixin",
        "spp.change.request.validation.sequence.mixin",
    ]
    _description = "Add Group Change Request Type"
    _order = "id desc"

    # Initialize DMS Storage
    DMS_STORAGE = "spp_change_request_add_group.attachment_storage_add_group"
    VALIDATION_FORM = (
        "spp_change_request_add_group.view_change_request_add_group_validation_form"
    )
    REQUIRED_DOCUMENT_TYPE = []
    IS_GROUP = False
    REGISTRAR_IS_APPLICANT = True

    # Mandatory initialize source and destination center areas
    # If validators will be allowed for both, make the values the same
    SRC_AREA_FLD = ["registrant_id", "area_center_id"]
    DST_AREA_FLD = SRC_AREA_FLD

    # Redefine registrant_id to set specific domain and label
    registrant_id = fields.Many2one(
        "res.partner",
        "Add to Group",
        domain=[("is_registrant", "=", True), ("is_group", "=", False)],
    )

    request_type = fields.Selection(related="change_request_id.request_type")

    # Change Request Fields
    name = fields.Char()

    phone = fields.Char("Phone Number")

    kind = fields.Many2one("g2p.group.kind", string="Group Type")

    # Add domain to inherited field: validation_ids
    validation_ids = fields.Many2many(
        relation="spp_change_request_add_group_rel",
        domain=[("request_type", "=", _name)],
    )

    @api.onchange("registrant_id")
    def _onchange_registrant_id(self):
        pass

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

    def validate_data(self):
        super().validate_data()
        if not self.name:
            raise ValidationError(_("The Name is required."))

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
        individual_id = self.env["res.partner"].create(
            {
                "is_registrant": True,
                "is_group": True,
                "name": self.name,
                "phone_number_ids": phone_rec,
                "kind": self.kind.id,
            }
        )
        individual_id.phone_number_ids_change()

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
                "name": _("Individual Details"),
                "views": [(form_id, "form")],
                "res_id": res_id,
                "target": "new",
                "context": context,
                "flags": {"mode": "readonly"},
            }
        )
        return action
