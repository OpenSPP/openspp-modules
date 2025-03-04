import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

RES_PARTNER = "res.partner"
CHANGE_REQUEST_EDIT_FARM = "spp.change.request.edit.farm"
FARM_ACTIVITY = "spp.farm.activity"
FARM_ASSET = "spp.farm.asset"


class ChangeRequestTypeCustomEditFarm(models.Model):
    _inherit = "spp.change.request"  # Not merging classes as it might require significant refactoring.

    registrant_id = fields.Many2one(
        RES_PARTNER,
        "Registrant",
        domain=[("is_registrant", "=", True), ("is_group", "=", True)],
    )

    def _check_phone_exist(self):
        """
        Checks if phone is existing

        :raise UserError: Exception raised when applicant_phone is not existing.
        """
        if not self.applicant_phone and "farm" not in self.request_type:
            raise UserError(_("Phone No. is required."))

    @api.model
    def _selection_request_type_ref_id(self):
        selection = super()._selection_request_type_ref_id()
        new_request_type = (CHANGE_REQUEST_EDIT_FARM, "Edit Farm")
        if new_request_type not in selection:
            selection.append(new_request_type)
        return selection


class ChangeRequestEditFarm(models.Model):
    _name = CHANGE_REQUEST_EDIT_FARM
    _inherit = [
        "spp.change.request.source.mixin",
        "spp.change.request.validation.sequence.mixin",
    ]
    _description = "Edit Farm Change Request Type"
    _order = "id desc"

    # Initialize CR constants
    VALIDATION_FORM = "spp_change_request_edit_farm.view_change_request_edit_farm_validation_form"
    REQUIRED_DOCUMENT_TYPE = [
        "spp_change_request_edit_farm.spp_dms_edit_farm",
    ]

    FARM_FIELDS = [
        "group_name",
        "group_kind",
        "land_name",
        "land_acreage",
        "land_coordinates",
        "land_geo_polygon",
        "details_legal_status",
    ]

    RES_PARTNER_FIELDS = [
        "name",
        "kind",
        "land_name",
        "land_acreage",
        "land_coordinates",
        "land_geo_polygon",
        "details_legal_status",
    ]

    # Mandatory initialize source and destination center areas
    # If validators will be allowed for both, make the values the same
    SRC_AREA_FLD = ["registrant_id", "area_center_id"]
    DST_AREA_FLD = SRC_AREA_FLD

    def _get_dynamic_selection(self):
        options = self.env["gender.type"].search([])
        return [(option.value, option.code) for option in options]

    registrant_id = fields.Many2one(
        RES_PARTNER,
        "Add to Group",
        domain=[("is_registrant", "=", True), ("is_group", "=", True)],
    )

    request_type = fields.Selection(related="change_request_id.request_type")

    # For ID Scanner Widget
    id_document_details = fields.Text("ID Document")

    # Group Details
    group_name = fields.Char("Group Name")
    group_kind = fields.Many2one(
        "g2p.group.kind",
        string="Group Kind",
        default=lambda self: self.env.ref("spp_farmer_registry_base.kind_farm", raise_if_not_found=False),
    )
    farm_crop_act_ids = fields.One2many(FARM_ACTIVITY, "crop_cr_edit_farm_id", string="Crop Agricultural Activities")
    farm_live_act_ids = fields.One2many(
        FARM_ACTIVITY, "live_cr_edit_farm_id", string="Livestock Agricultural Activities"
    )
    farm_aqua_act_ids = fields.One2many(
        FARM_ACTIVITY,
        "aqua_cr_edit_farm_id",
        string="Aquaculture Agricultural Activities",
    )
    farm_asset_ids = fields.One2many(FARM_ASSET, "asset_cr_edit_farm_id", string="Farm Assets")
    farm_machinery_ids = fields.One2many(FARM_ASSET, "machinery_cr_edit_farm_id", string="Farm Machinery")

    # Land Record
    land_name = fields.Char(string="Parcel Name/ID")
    land_acreage = fields.Float()
    land_coordinates = fields.GeoPointField()
    land_geo_polygon = fields.GeoPolygonField(string="Land Polygons")

    # Farm Details
    details_legal_status = fields.Selection(
        [
            ("self", "Owned by self"),
            ("family", "Owned by family"),
            ("extended community", "Owned by extended community"),
            ("cooperative", "Owned by cooperative"),
            ("government", "Owned by Government"),
            ("leased", "Leased from actual owner"),
            ("unknown", "Do not Know"),
        ],
        string="Legal Status",
    )

    # Add domain to inherited field: validation_ids
    validation_ids = fields.Many2many(
        relation="spp_change_request_edit_farm_rel",
        domain=[("request_type", "=", _name)],
    )

    # DMS Field
    dms_directory_ids = fields.One2many(
        "spp.dms.directory",
        "change_request_edit_farm_id",
        string="DMS Directories",
        auto_join=True,
    )
    dms_file_ids = fields.One2many(
        "spp.dms.file",
        "change_request_edit_farm_id",
        string="DMS Files",
        auto_join=True,
    )

    @api.onchange("registrant_id")
    def _onchange_registrant_id(self):
        """
        Handles changes to the registrant_id field.
        Currently a placeholder for future implementation.
        """
        return

    @api.onchange("id_document_details")
    def _onchange_scan_id_document_details(self):
        """
        Handles changes to the id_document_details field.
        Currently a placeholder for future implementation.
        """
        return

    def _get_default_change_request_id(self):
        """
        Returns the default field name for change request id.

        Returns:
            str: The default field name 'default_change_request_edit_farm_id'
        """
        return "default_change_request_edit_farm_id"

    def validate_data(self):
        """
        Validates the change request data.

        Raises:
            ValidationError: If the registrant_id (Group or Farm) is not set

        Returns:
            bool: Result of the parent class's validate_data method
        """
        validate_data = super().validate_data()
        error_message = []
        if not self.registrant_id:
            error_message.append(_("The Group or Farm is required!"))
        if error_message:
            raise ValidationError("\n".join(error_message))

        return validate_data

    def update_live_data(self):
        """
        Updates the live data for the farm/group after change request approval.

        This method:
        1. Updates the group (res.partner) with new field values
        2. Updates related records (activities and assets) with new relationships
        3. Updates the change request with group and applicant information

        Returns:
            res.partner: The updated group record
        """
        self.ensure_one()

        # Update the group (res.partner)

        group_vals = {
            "is_registrant": True,
            "is_group": True,
        }
        for farm_field, res_partner_field in zip(self.FARM_FIELDS, self.RES_PARTNER_FIELDS, strict=True):
            if self[farm_field]:
                group_vals[res_partner_field] = self[farm_field]

        group = self.registrant_id
        group.write(group_vals)

        # Define mapping of One2many fields to their target fields
        activity_mappings = {
            "farm_crop_act_ids": "crop_farm_id",
            "farm_live_act_ids": "live_farm_id",
            "farm_aqua_act_ids": "aqua_farm_id",
            "farm_asset_ids": "asset_farm_id",
            "farm_machinery_ids": "machinery_farm_id",
        }

        # Update related records
        for source_field, target_field in activity_mappings.items():
            if records := self[source_field]:
                records.write({target_field: group.id})

        cr_vals = {
            "registrant_id": group.id,
        }
        if group.group_membership_ids:
            cr_vals["applicant_id"] = group.group_membership_ids[0].individual.id

        self.change_request_id.write(cr_vals)

        return group

    def open_registrant_details_form(self):
        """
        Opens a form view showing the registrant's details in readonly mode.

        Returns:
            dict: Action dictionary for opening the form view
        """
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


class ChangeRequestEditFarmAgriculturalActivity(models.Model):
    _inherit = FARM_ACTIVITY

    crop_cr_edit_farm_id = fields.Many2one(CHANGE_REQUEST_EDIT_FARM, string="Crop Farm")
    live_cr_edit_farm_id = fields.Many2one(CHANGE_REQUEST_EDIT_FARM, string="Livestock Farm")
    aqua_cr_edit_farm_id = fields.Many2one(CHANGE_REQUEST_EDIT_FARM, string="Aqua Farm")


class ChangeRequestEditFarmAssets(models.Model):
    _inherit = FARM_ASSET

    asset_cr_edit_farm_id = fields.Many2one(CHANGE_REQUEST_EDIT_FARM, string="Asset Farm")
    machinery_cr_edit_farm_id = fields.Many2one(CHANGE_REQUEST_EDIT_FARM, string="Machinery Farm")
