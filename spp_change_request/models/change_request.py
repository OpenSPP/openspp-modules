# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import json
import logging

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ChangeRequestBase(models.Model):
    _name = "spp.change.request"
    _description = "Change Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"
    _check_company_auto = True

    def _default_name(self):
        name = self.env["ir.sequence"].next_by_code("spp.change.request.num")
        return name

    name = fields.Char("Request #", required=True, default=_default_name)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    date_requested = fields.Datetime()
    request_type = fields.Selection(
        selection="_selection_request_type_ref_id", required=True
    )
    registrant_id = fields.Many2one(
        "res.partner",
        "Registrant",
        domain=[("is_registrant", "=", True), ("is_group", "=", True)],
    )
    applicant_id = fields.Many2one(
        "res.partner",
        "Applicant",
        domain=[("is_registrant", "=", True), ("is_group", "=", False)],
    )
    applicant_id_domain = fields.Char(
        compute="_compute_applicant_id_domain",
        readonly=True,
        store=False,
    )
    applicant_unified_id = fields.Char("Applicant's UID Number")
    applicant_phone = fields.Char("Applicant's Phone Number")

    request_type_ref_id = fields.Reference(
        string="Change Request Template", selection="_selection_request_type_ref_id"
    )
    validator_ids = fields.One2many(
        "spp.change.request.validators", "request_id", "Validation Records"
    )
    assign_to_id = fields.Many2one("res.users", "Assigned to")
    last_validated_by_id = fields.Many2one("res.users", "Validated by")
    date_validated = fields.Datetime()
    applied_by_id = fields.Many2one("res.users", "Applied by")
    date_applied = fields.Datetime()
    last_activity_id = fields.Many2one("mail.activity")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending", "Pending Validation"),
            ("validated", "Validated"),
            ("applied", "Applied"),
            ("rejected", "Rejected"),
        ],
        "Status",
        required=True,
        readonly=True,
        default="draft",
    )

    @api.model
    def create(self, vals):
        res = super(ChangeRequestBase, self).create(vals)
        # Create pending validation activity
        activity_type = "spp_change_request.pending_validation_activity"
        summary = _("For Pending Validation")
        note = _(
            "A new change request was submitted. The next step will set this request to 'Pending Validation'."
        )
        activity = res._generate_activity(activity_type, summary, note)
        res["last_activity_id"] = activity.id
        return res

    @api.model
    def _selection_request_type_ref_id(self):
        return []

    @api.depends("registrant_id")
    def _compute_applicant_id_domain(self):
        for rec in self:
            domain = [("id", "=", 0)]
            if rec.registrant_id:
                group_membership_ids = rec.registrant_id.group_membership_ids.mapped(
                    "individual.id"
                )
                domain = [("id", "in", group_membership_ids)]
            rec.applicant_id_domain = json.dumps(domain)

    @api.onchange("applicant_id")
    def _onchange_applicant_id(self):
        if self.applicant_id:
            vals = {
                "applicant_unified_id": self.applicant_id.unified_id,
                "applicant_phone": self.applicant_id.phone,
            }
            self.update(vals)

    def open_change_request_form(self, target="current", mode="readonly"):
        self.ensure_one()
        if self.request_type_ref_id:
            # Get the res_model and res_id from the request_type_ref_id (reference field)
            request_type_ref_id = str(self.request_type_ref_id)
            s = request_type_ref_id.find("(")
            res_model = request_type_ref_id[:s]
            res_id = self.request_type_ref_id.id
            if res_id:
                form_id = self.env[res_model].get_request_type_view_id()
                if self._context.get("show_validation_form"):
                    form = (
                        self.env.ref(self.request_type_ref_id.VALIDATION_FORM) or None
                    )
                    if form:
                        form_id = form.id
                action = self.env[res_model].get_formview_action()
                context = {
                    "create": False,
                }
                action.update(
                    {
                        "views": [(form_id, "form")],
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
                "title": _("ERROR!"),
                "message": _("The Request Type field must be filled-up."),
                "sticky": False,
                "type": "danger",
            },
        }

    def open_applicant_form(self, target="current", mode="readonly"):
        self.ensure_one()
        if self.applicant_id:
            res_id = self.applicant_id.id
            form_id = self.env.ref("g2p_registry_individual.view_individuals_form").id
            action = self.env["res.partner"].get_formview_action()
            context = {
                "create": False,
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
        for rec in self:
            # Open Request Form
            return rec.open_change_request_form(target="current", mode="edit")

    def create_request_detail(self):
        for rec in self:
            if rec.state in ("draft", "pending"):
                # Set the request_type_ref_id
                res_model = rec.request_type
                # Set the dms directory
                _logger.info(
                    "Change Request: DMS Directory Creation (%s)"
                    % len(self.dms_directory_ids)
                )
                storage = self.env.ref(self.env[res_model].DMS_STORAGE)
                dmsval = {
                    "storage_id": storage.id,
                    # "res_id": rec.id,
                    "res_model": res_model,
                    "is_root_directory": True,
                    "name": rec.name,
                    "group_ids": [(4, storage.field_default_group_id.id)],
                }

                # Create the change request detail record
                ref_id = self.env[res_model].create(
                    {
                        "registrant_id": rec.registrant_id.id,
                        "applicant_id": rec.applicant_id.id,
                        "change_request_id": rec.id,
                        "dms_directory_ids": [(Command.create(dmsval))],
                    }
                )
                ref_id._onchange_registrant_id()
                request_type_ref_id = f"{res_model},{ref_id.id}"
                _logger.debug("DEBUG! request_type_ref_id: %s", request_type_ref_id)
                rec.update(
                    {
                        "request_type_ref_id": request_type_ref_id,
                    }
                )
                # Open Request Form
                return rec.open_change_request_form(target="current", mode="edit")
            else:
                raise UserError(
                    _(
                        "The change request to be created must be in draft or pending validation state."
                    )
                )

    def on_submit(self):
        for rec in self:
            if rec.request_type_ref_id:
                if rec.state == "draft":
                    rec.request_type_ref_id._on_submit(rec)
                else:
                    raise UserError(
                        _(
                            "The request must be in draft state to be set to pending validation."
                        )
                    )
            else:
                raise UserError(
                    _("The change request type must be properly filled-up.")
                )

    def on_validate(self):
        for rec in self:
            # Check if change user is assigned to current user
            if rec._check_user("Validate"):
                if rec.request_type_ref_id:
                    if rec.state == "pending":
                        rec.request_type_ref_id._on_validate(rec)
                    else:
                        raise ValidationError(
                            _("The request to be validated must be in submitted state.")
                        )
                else:
                    raise UserError(
                        _("The request details must be properly filled-up.")
                    )

    def apply(self):
        for rec in self:
            # Check if change user is assigned to current user
            if rec._check_user("Apply"):
                if rec.state == "validated":
                    rec.request_type_ref_id._apply(rec)
                else:
                    raise ValidationError(
                        _(
                            "The request must be in validated state for changes to be applied."
                        )
                    )

    def on_reject(self):
        for rec in self:
            # Check if change user is assigned to current user
            if rec._check_user("Reject"):
                if rec.state in ("draft", "pending"):
                    rec.request_type_ref_id._on_reject(rec)
                else:
                    raise UserError(
                        _(
                            "The request to be rejected must be in draft or pending validation state."
                        )
                    )

    def _check_user(self, process):
        self.ensure_one()
        if self.assign_to_id:
            if self.assign_to_id.id == self.env.user.id:
                return True
            else:
                raise UserError(
                    _("You are not allowed to %s this change request", process)
                )
        else:
            raise UserError(_("There are no user assigned to this change request."))

    def _get_validation_stage(self):
        self.ensure_one()
        stage = None
        message = None
        validator_id = self.env.user.id
        # Get the current validators
        validation_stages = None
        validation_stage_ids = None
        if self.validator_ids:
            validation_stage_ids = self.validator_ids.mapped("stage_id.id")
        if self.request_type_ref_id.validation_ids:
            # Get the next validation sequence
            if validation_stage_ids:
                validation_stages = self.request_type_ref_id.validation_ids.filtered(
                    lambda a: a.stage_id.id not in validation_stage_ids
                )
            else:
                validation_stages = self.request_type_ref_id.validation_ids
            if validation_stages:
                if len(validation_stages) == 1:
                    message = "FINAL"
                stage = validation_stages[0]
                # Check if user is allowed to validate request
                if validator_id not in stage.validation_group_id.users.ids:
                    message = _(
                        "You are not allowed to validate this request! Stage: %s",
                        stage.stage_id.name,
                    )
                    stage = None
            else:
                message = _(
                    "Error in validation stages. No available stage to assign to this validation."
                )
        else:
            message = _("There are no validators defined for this request.")
        return stage, message, validator_id

    def _generate_activity(self, activity_type, summary, note):
        self.ensure_one()
        activity_type_id = self.env.ref(activity_type).id
        next_activity = {
            "res_id": self.id,
            "res_model_id": self.env["ir.model"]._get(self._name).id,
            "user_id": self.env.user.id,
            "summary": summary,
            "note": note,
            "activity_type_id": activity_type_id,
            "date_deadline": fields.Date.today(),
        }
        return self.env["mail.activity"].create(next_activity)


class ChangeRequestValidators(models.Model):
    _name = "spp.change.request.validators"
    _description = "Change Request Validators"
    _rec_name = "validator_id"

    request_id = fields.Many2one("spp.change.request", "Change Request", required=True)
    stage_id = fields.Many2one(
        "spp.change.request.validation.stage", "Validation Stage", required=True
    )
    validator_id = fields.Many2one("res.users", "Validated by", required=True)
    date_validated = fields.Datetime()


class ChangeRequestValidationSequence(models.Model):
    _name = "spp.change.request.validation.sequence"
    _description = "Change Request Validation Sequence"
    _rec_name = "stage_id"
    _order = "sequence,id"

    sequence = fields.Integer(default=10)
    request_type = fields.Selection(
        selection="_selection_request_type_ref_id", required=True
    )
    stage_id = fields.Many2one(
        "spp.change.request.validation.stage", "Validation Stage", required=True
    )
    validation_group_id = fields.Many2one(
        "res.groups", string="Change Request Validation Group"
    )

    @api.model
    def _selection_request_type_ref_id(self):
        return []
