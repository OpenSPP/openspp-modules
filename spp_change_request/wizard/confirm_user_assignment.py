# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ConfirmUserAssignmentWiz(models.TransientModel):
    _name = "spp.change.request.user.assign.wizard"
    _description = "Change Request User Assignment Wizard"

    @api.model
    def default_get(self, fields):
        # TODO: Skip if CR is not assigned to anybody. The user will be automatically assigned.
        res = super(ConfirmUserAssignmentWiz, self).default_get(fields)
        if self.env.context.get("change_request_id"):
            res["change_request_id"] = self.env.context["change_request_id"]
        else:
            if self.env.context.get("active_id"):
                res["change_request_id"] = self.env.context["active_id"]
        if self.env.context.get("curr_assign_to_id"):
            if self.env.context["curr_assign_to_id"] != self.env.user.id:
                res["assign_to_id"] = self.env.user
            res["curr_assign_to_id"] = self.env.context["curr_assign_to_id"]
        else:
            res["assign_to_id"] = self.env.user.id
        return res

    change_request_id = fields.Many2one(
        "spp.change.request", "Change Request", required=True
    )
    curr_assign_to_id = fields.Many2one(
        "res.users", "Currently Assigned to", related="change_request_id.assign_to_id"
    )
    assign_to_id = fields.Many2one("res.users", "Transfer to")
    dialog_message = fields.Text(compute="_compute_message_assignment")
    assign_to_any = fields.Boolean(compute="_compute_message_assignment")

    def assign_to_user(self):
        for rec in self:
            # Check if user is a member of validators in the validation sequence config
            user_ok = False
            if rec.change_request_id.request_type_ref_id.validation_ids:
                for mrec in rec.change_request_id.request_type_ref_id.validation_ids:
                    if mrec.validation_group_id.id in rec.assign_to_id.groups_id.ids:
                        user_ok = True
                        break
                if user_ok:
                    rec.change_request_id.update(
                        {
                            "assign_to_id": rec.assign_to_id.id,
                        }
                    )
                else:
                    raise UserError(
                        _(
                            "Only users of groups defined in the validation sequence "
                            "can be assigned to this change request."
                        )
                    )
            else:
                raise UserError(
                    _(
                        "This change request does not have any validation sequence defined."
                    )
                )

    @api.depends("change_request_id", "assign_to_id")
    def _compute_message_assignment(self):
        for rec in self:
            assign_to_any = False
            if not rec.curr_assign_to_id:
                # No user assignment
                msg1 = _(
                    "The change request: %s is not assigned to any user.",
                    rec.change_request_id.name,
                )
            elif rec.curr_assign_to_id.id == self.env.user.id:
                # The current assigned user is the current user
                msg1 = _(
                    "The change request: %s is currently assigned to you.",
                    rec.change_request_id.name,
                )
            else:
                msg1 = _(
                    f"The change request: {rec.change_request_id.name} "
                    "is currently assigned to {rec.curr_assign_to_id.name}."
                )
            if rec.assign_to_id.id == self.env.user.id:
                # Assign to current user
                msg2 = _("Are you sure you would like to assign this to yourself?")
            else:
                msg2 = _("Are you sure you would like to assign this to:")
                assign_to_any = True
            rec.update(
                {
                    "dialog_message": f"{msg1} {msg2}",
                    "assign_to_any": assign_to_any,
                }
            )
