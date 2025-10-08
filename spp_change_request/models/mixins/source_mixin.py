# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import _, fields, models

_logger = logging.getLogger(__name__)


class ChangeRequestSourceMixin(models.AbstractModel):
    """
    Change Request Data Source mixin.
    ---------------------------------
    This mixin is inherited by objects implementing a change Request.

    Example:

    .. code-block:: python

        class ChangeRequestAddChildren(models.Model):
            _name = "spp.change.request.demo.add.children"
            _inherit = [
                "spp.change.request.source.mixin",
                "spp.change.request.validation.sequence.mixin",
            ]
            _description = "Add Children Change Request Type"

            # Initialize DMS Storage
            DMS_STORAGE = "spp_change_request_add_children.attachment_storage_add_children"
            VALIDATION_FORM = "spp_change_request_add_children.view_change_request_add_children_validation_form"
            REQUIRED_DOCUMENT_TYPE = [
                "change_request.dms_birth_certificate_category",
            ]

    """

    _inherit = "spp.change.request.source.mixin"

    REQUIRED_DOCUMENT_TYPE = []  # List of required document category `spp.dms.category`
    VALIDATION_FORM = None
    AUTO_APPLY_CHANGES = True

    registrant_id = fields.Many2one("res.partner", "Registrant", domain=[("is_registrant", "=", True)])
    applicant_id = fields.Many2one(
        "res.partner",
        "Applicant",
        domain=[("is_registrant", "=", True), ("is_group", "=", False)],
    )
    applicant_phone = fields.Char("Applicant's Phone Number", related="change_request_id.applicant_phone")
    change_request_id = fields.Many2one("spp.change.request", "Change Request", required=True)
    assign_to_id = fields.Many2one("res.users", "Assigned to", related="change_request_id.assign_to_id")
    last_validated_by_id = fields.Many2one(
        "res.users", "Last Validator", related="change_request_id.last_validated_by_id"
    )
    date_validated = fields.Datetime(related="change_request_id.date_validated")
    state = fields.Selection(
        related="change_request_id.state",
        string="Status",
        readonly=True,
    )

    # Target Fields
    group_address = fields.Text(related="registrant_id.address", readonly=True)
    group_registration_date = fields.Date(related="registrant_id.registration_date", readonly=True)

    # DMS Field
    # dms_directory_ids = fields.One2many(
    #    "spp.dms.directory",
    #    "change_request_id",
    #    string="DMS Directories",
    #    auto_join=True,
    # )
    # dms_file_ids = fields.One2many(
    #    "spp.dms.file",
    #    "change_request_id",
    #    string="DMS Files",
    #    auto_join=True,
    # )
    validation_stage = fields.Selection(
        string="Validation Stage",
        related="change_request_id.validation_stage",
    )
    show_cr_actions = fields.Boolean(compute="_compute_show_cr_actions")
    show_assign_button = fields.Boolean(compute="_compute_show_assign_button")
    show_reassign_button = fields.Boolean(compute="_compute_show_reassign_button")

    def _compute_show_cr_actions(self):
        for rec in self:
            user = self.env.user
            rec.show_cr_actions = (
                rec.validation_stage == "local"
                and user.has_group("spp_change_request.group_spp_change_request_validator")
                and user.id == rec.assign_to_id.id
            ) or (
                rec.validation_stage == "hq"
                and user.has_group("spp_change_request.group_spp_change_request_hq_validator")
                and user.id == rec.assign_to_id.id
            )
    
    def _compute_show_assign_button(self):
        for rec in self:
            user = self.env.user
            assigned_id = rec.assign_to_id.id if rec.assign_to_id else None
            user_not_assigned = True if assigned_id and assigned_id != user.id else False
            rec.show_assign_button = (
                rec.state in ("draft", "pending", "validated", "rejected")
                and (
                    rec.validation_stage == "local"
                    and user.has_group("spp_change_request.group_spp_change_request_validator")
                ) or (
                    rec.validation_stage == "hq"
                    and user.has_group("spp_change_request.group_spp_change_request_hq_validator")
                ) and (user_not_assigned or not rec.assign_to_id) or user.has_group("g2p_registry_base.group_g2p_admin")
            )
    
    def _compute_show_reassign_button(self):
        for rec in self:
            user = self.env.user
            rec.show_reassign_button = (
                rec.state in ("draft", "pending", "validated", "rejected")
                and (
                    rec.validation_stage == "local"
                    and user.has_group("spp_change_request.group_spp_change_request_validator")
                ) or (
                    rec.validation_stage == "hq"
                    and user.has_group("spp_change_request.group_spp_change_request_hq_validator")
                ) or user.has_group("g2p_registry_base.group_g2p_admin")
            ) and rec.assign_to_id.id == user.id

    def _copy_group_member_ids(self, group_id_field, group_ref_field="registrant_id"):
        for rec in self:
            for mrec in rec[group_ref_field].group_membership_ids:
                kind_ids = mrec.kind and mrec.kind.ids or None
                group_members = {
                    group_id_field: rec.id,
                    "individual_id": mrec.individual.id,
                    "kind_ids": kind_ids,
                }
                self.env["spp.change.request.group.members"].create(group_members)

    def copy_group_member_ids_condition(self):
        """Conditions to copy group members

        Overwrite this function to the inherited model to add
        condition when copying a group member.
        Do not overwrite or override if no conditions needed.

        example:
            def copy_group_member_ids_condition:
                if self.state == 'draft':
                    return True
                return False

        NOTE: always return True or False
        """
        return True

    def copy_group_member_ids(
        self,
        group_id_field,
        group_ref_field="registrant_id",
        model_name="spp.change.request.group.members",
        condition_function=copy_group_member_ids_condition,
    ):
        """Copy group members

        :param group_id_field str: name of the field
        :param group_ref_field str: name of the reference field, default value is 'registrant_id'
        :param model_name str/list: name or list of model names, default value is 'spp.change.request.group.members'
        :param condition_function method: method to add conditions, default value is copy_group_member_ids_condition

        :return:

        :example:
            self.copy_group_member_ids("group_member_id")
            self.copy_group_member_ids("group_member_id", group_ref_field="registrant_id")
            self.copy_group_member_ids("group_member_id", model_name="spp.change.request")

            def my_condition(self):
                if self.state == 'draft':
                    return True
                return False

            self.copy_group_member_ids("group_member_id", condition_function=my_condition)

        """
        for rec in self:
            for mrec in rec[group_ref_field].group_membership_ids:
                kind_ids = mrec.kind and mrec.kind.ids or None
                if condition_function(self):
                    group_members = {
                        group_id_field: rec.id,
                        "individual_id": mrec.individual.id,
                        "kind_ids": kind_ids,
                    }
                    if isinstance(model_name, str):
                        self.env[model_name].create(group_members)
                    else:
                        for model in model_name:
                            self.env[model].create(group_members)

    def open_applicant_details_form(self):
        """
        Get and opens the form view of the applicant_id to view details

        Usage:
        - Add this function in the name of button with type object in XML

        example:
            <button
                name="open_applicant_details_form"
                type="object"
            />

        NOTE:
        - To add or modify some key-value pair, either call or super this function

        example:
            def open_applicant_details_form(self):
                action = super().open_applicant_details_form()

                action.update({'key': 'value'})

                return action

        :return dict action: form view action

        :raise:
        """
        self.ensure_one()
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

    def show_notification(self, title, message, kind):
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Change Request Validated"),
                "message": message,
                "next": {
                    "type": "ir.actions.act_window_close",
                },
                "sticky": True,
                "type": kind,
            },
        }
