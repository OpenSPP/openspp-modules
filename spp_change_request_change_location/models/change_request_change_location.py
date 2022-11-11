# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import Command, _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ChangeRequestTypeCustomChangeLocation(models.Model):
    _inherit = "spp.change.request"

    @api.model
    def _selection_request_type_ref_id(self):
        selection = super()._selection_request_type_ref_id()
        new_request_type = (
            "spp.change.request.change.location",
            "Change Branch/Centre/Food Agent",
        )
        if new_request_type not in selection:
            selection.append(new_request_type)
        return selection


class ChangeRequestChangeLocation(models.Model):
    _name = "spp.change.request.change.location"
    _inherit = [
        "spp.change.request.source.mixin",
        "spp.change.request.validation.sequence.mixin",
    ]
    _description = "Change Branch/Centre/Food Agent Change Request Type"

    # Initialize DMS Storage
    DMS_STORAGE = (
        "spp_change_request_change_location.attachment_storage_change_location"
    )
    VALIDATION_FORM = "spp_change_request_change_location.view_change_request_change_location_validation_form"

    # Redefine registrant_id to set specific domain and label
    registrant_id = fields.Many2one(
        "res.partner",
        "Group to Change Location",
        domain=[("is_registrant", "=", True), ("is_group", "=", True)],
    )

    request_type = fields.Selection(related="change_request_id.request_type")

    # Change Request Fields
    change_to_area_center_id = fields.Many2one("spp.area", "Center Area")
    remarks = fields.Text()

    # Current Registrant Information
    area_center_id = fields.Many2one(
        "spp.area", "Center Area", related="registrant_id.area_center_id"
    )

    # Add domain to inherited field: validation_ids
    validation_ids = fields.Many2many(
        relation="spp_change_request_chg_loc_rel", domain=[("request_type", "=", _name)]
    )

    def write(self, vals):
        res = super(ChangeRequestChangeLocation, self).write(vals)
        if self.registrant_id:
            # Must update the spp.change.request (base) registrant_id
            self._update_registrant_id(self)
        return res

    def _update_live_data(self):
        # TODO: Update the live data
        self.ensure_one()

    def _on_validate(self, request):
        self.ensure_one()
        # Get current validation sequence
        stage, message, validator_id = request._get_validation_stage()
        if stage:
            validator = {
                "stage_id": stage.id,
                "validator_id": validator_id,
                "date_validated": fields.Datetime.now(),
            }
            vals = {
                "validator_ids": [(Command.create(validator))],
                "validatedby_id": validator_id,
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

    def open_registrant_details_form(self):
        self.ensure_one()
        res_id = self.registrant_id.id
        form_id = self.env.ref("g2p_registry_group.view_groups_form").id
        action = self.env["res.partner"].get_formview_action()
        context = {
            "create": False,
            "edit": False,
        }
        action.update(
            {
                "name": _("Member Details"),
                "views": [(form_id, "form")],
                "res_id": res_id,
                "target": "new",
                "context": context,
                "flags": {"mode": "readonly"},
            }
        )
        return action
