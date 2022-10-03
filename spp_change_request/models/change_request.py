# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ChangeRequestBase(models.Model):
    _name = "spp.change.request"
    _description = "Area"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"
    _check_company_auto = True

    name = fields.Char("Request #", required=True, default="Draft")
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    date_requested = fields.Datetime()
    request_type = fields.Selection(
        string="Request Type", selection="_selection_request_type_ref_id", required=True
    )
    registrant_id = fields.Many2one(
        "res.partner",
        "Registrant",
        domain=[("is_registrant", "=", True)],
        required=True,
    )
    request_type_ref_id = fields.Reference(
        string="Change Request Template", selection="_selection_request_type_ref_id"
    )
    validator_id = fields.Many2one("res.users", "Validated by")
    date_validated = fields.Datetime()
    approver_id = fields.Many2one("res.users", "Approved by")
    date_approved = fields.Datetime()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("validated", "Validated"),
            ("approved", "Approved"),
            ("cancelled", "Cancelled"),
        ],
        "status",
        required=True,
        readonly=True,
        default="draft",
    )

    @api.model
    def _selection_request_type_ref_id(self):
        return []

    def open_change_request_form(self, target="current", mode="readonly"):
        self.ensure_one()
        if self.request_type_ref_id:
            # Get the res_model and res_id from the request_type_ref_id (reference field)
            request_type_ref_id = str(self.request_type_ref_id)
            s = request_type_ref_id.find("(")
            res_model = request_type_ref_id[:s]
            res_id = self.request_type_ref_id.id
            if res_id:
                action = self.env[res_model].get_formview_action()
                context = {
                    "create": False,
                }
                action.update(
                    {
                        "views": [
                            (self.env[res_model].get_request_type_view_id(), "form")
                        ],
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
                "title": "ERROR!",
                "message": "The Request Type field must be filled-up.",
                "sticky": False,
                "type": "danger",
            },
        }

    def open_request_detail(self):
        for rec in self:
            # Open Request Form
            return rec.open_change_request_form(target="new", mode="edit")

    def create_request_detail(self):
        for rec in self:
            if rec.state == "draft":
                # Set the request_type_ref_id
                res_model = rec.request_type
                ref_id = self.env[res_model].create(
                    {"registrant_id": rec.registrant_id.id, "change_request_id": rec.id}
                )
                request_type_ref_id = f"{res_model},{ref_id.id}"
                _logger.debug("DEBUG! request_type_ref_id: %s", request_type_ref_id)
                rec.update(
                    {
                        "request_type_ref_id": request_type_ref_id,
                    }
                )
                # Open Request Form
                return rec.open_change_request_form(target="new", mode="edit")
            else:
                raise ValidationError(
                    _("The change request to be created must be in draft state.")
                )

    def submit_request(self):
        for rec in self:
            if rec.state == "draft":
                name = self.env["ir.sequence"].next_by_code("spp.change.request.num")
                rec.update(
                    {
                        "name": name,
                        "date_requested": fields.Datetime.now(),
                        "state": "submitted",
                    }
                )
            else:
                raise ValidationError(
                    _("The request to be submitted must be in draft state.")
                )

    def validate_request(self):
        for rec in self:
            if rec.state == "submitted":
                rec.update(
                    {
                        "validator_id": self.env.user,
                        "date_validated": fields.Datetime.now(),
                        "state": "validated",
                    }
                )
            else:
                raise ValidationError(
                    _("The request to be validated must be in submitted state.")
                )

    def approve_request(self):
        for rec in self:
            if rec.state == "validated":
                # Apply Changes to Live Data
                rec.request_type_ref_id.update_live_data()
                # Update CR record
                rec.update(
                    {
                        "approver_id": self.env.user,
                        "date_approved": fields.Datetime.now(),
                        "state": "approved",
                    }
                )
            else:
                raise ValidationError(
                    _("The request to be approved must be in validated state.")
                )

    def cancel_request(self):
        for rec in self:
            if rec.state in ("draft", "submitted"):
                rec.update(
                    {
                        "state": "cancelled",
                    }
                )
            else:
                raise ValidationError(
                    _(
                        "The request to be cancelled must be in draft or submitted state."
                    )
                )
