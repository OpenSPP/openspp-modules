# Part of Newlogic G2P. See LICENSE file for full copyright and licensing details.

import logging

from odoo import _, api, fields, models

from . import constants

_logger = logging.getLogger(__name__)


class G2PCycle(models.Model):
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _name = "g2p.cycle"
    _description = "Cycle"
    _order = "sequence asc"
    _check_company_auto = True

    STATE_DRAFT = constants.STATE_DRAFT
    STATE_TO_APPROVE = constants.STATE_TO_APPROVE
    STATE_APPROVED = constants.STATE_APPROVED
    STATE_CANCELED = constants.STATE_CANCELLED
    STATE_DISTRIBUTED = constants.STATE_DISTRIBUTED
    STATE_ENDED = constants.STATE_ENDED

    name = fields.Char(required=True)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    program_id = fields.Many2one("g2p.program", "Program", required=True)
    sequence = fields.Integer(required=True, readonly=True, default=1)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    state = fields.Selection(
        [
            (STATE_DRAFT, "Draft"),
            (STATE_TO_APPROVE, "To Approve"),
            (STATE_APPROVED, "Approved"),
            (STATE_DISTRIBUTED, "Distributed"),
            (STATE_CANCELED, "Canceled"),
            (STATE_ENDED, "Ended"),
        ],
        default="draft",
    )

    cycle_membership_ids = fields.One2many(
        "g2p.cycle.membership", "cycle_id", "Cycle Memberships"
    )
    entitlement_ids = fields.One2many("g2p.entitlement", "cycle_id", "Entitlements")

    # Statistics
    members_count = fields.Integer(
        string="# Beneficiaries", compute="_compute_members_count"
    )
    entitlements_count = fields.Integer(
        string="# Entitlements", compute="_compute_entitlements_count"
    )

    @api.depends("cycle_membership_ids")
    def _compute_members_count(self):
        for rec in self:
            members_count = 0
            if rec.cycle_membership_ids:
                members_count = len(
                    rec.cycle_membership_ids.filtered(lambda mb: mb.state == "enrolled")
                )
            rec.update({"members_count": members_count})

    @api.depends("entitlement_ids")
    def _compute_entitlements_count(self):
        for rec in self:
            entitlements_count = 0
            if rec.entitlement_ids:
                entitlements_count = len(rec.entitlement_ids)
            rec.update({"entitlements_count": entitlements_count})

    @api.onchange("start_date")
    def on_start_date_change(self):
        self.program_id.get_manager(constants.MANAGER_CYCLE).on_start_date_change(self)

    @api.onchange("state")
    def on_state_change(self):
        # _logger.info("DEBUG! state change: %s", self.state)
        self.program_id.get_manager(constants.MANAGER_CYCLE).on_state_change(self)

    @api.model
    def get_beneficiaries(self, state):
        if isinstance(state, str):
            state = [state]
        for rec in self:
            domain = [("state", "in", state), ("cycle_id", "=", rec.id)]
            return self.env["g2p.cycle.membership"].search(domain)

    # TODO: JJ - Add a way to link reports/Dashboard about this cycle.

    # TODO: Implement the method that will call the different managers

    # @api.model
    def copy_beneficiaries_from_program(self):
        # _logger.info("Copying beneficiaries from program, cycles: %s", cycles)
        self.ensure_one()
        self.program_id.get_manager(
            constants.MANAGER_CYCLE
        ).copy_beneficiaries_from_program(self)

    def check_eligibility(self, beneficiaries=None):
        self.program_id.get_manager(constants.MANAGER_CYCLE).check_eligibility(
            self, beneficiaries
        )

    def to_approve(self):
        for rec in self:
            if rec.state == self.STATE_DRAFT:
                rec.update({"state": self.STATE_TO_APPROVE})
            else:
                message = _("Ony 'draft' cycles can be set for approval.")
                kind = "danger"

                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Cycle"),
                        "message": message,
                        "sticky": True,
                        "type": kind,
                    },
                }

    def reset_draft(self):
        for rec in self:
            if rec.state == self.STATE_TO_APPROVE:
                rec.update({"state": self.STATE_DRAFT})
            else:
                message = _("Ony 'to approve' cycles can be reset to draft.")
                kind = "danger"

                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Cycle"),
                        "message": message,
                        "sticky": True,
                        "type": kind,
                    },
                }

    def approve(self):
        # 1. Make sure the user has the right to do this
        # 2. Approve the cycle using the cycle manager
        for rec in self:
            cycle_managers = self.program_id.get_manager(constants.MANAGER_CYCLE)

            auto_approve = False
            if cycle_managers.auto_approve_entitlements:
                auto_approve = True

            if auto_approve:
                entitlements = self.env["g2p.entitlement"].search(
                    [
                        ("cycle_id", "=", rec.id),
                        ("state", "=", "draft"),
                    ]
                )
                if entitlements:
                    for e in entitlements:
                        e.approve_entitlement()

            if rec.state == self.STATE_TO_APPROVE:
                rec.update({"state": self.STATE_APPROVED})
                # Running on_state_change because it is not triggered automatically with rec.update above
                rec.on_state_change()
            else:
                message = _("Ony 'to approve' cycles can be approved.")
                kind = "danger"

                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Cycle"),
                        "message": message,
                        "sticky": True,
                        "type": kind,
                    },
                }

    def notify_cycle_started(self):
        # 1. Notify the beneficiaries using notification_manager.cycle_started()
        pass

    def prepare_entitlement(self):
        # 1. Prepare the entitlement of the beneficiaries using entitlement_manager.prepare_entitlements()
        self.program_id.get_manager(constants.MANAGER_CYCLE).prepare_entitlements(self)

    def mark_distributed(self):
        # 1. Mark the cycle as distributed using the cycle manager
        self.program_id.get_manager(constants.MANAGER_CYCLE).mark_distributed(self)

    def mark_ended(self):
        # 1. Mark the cycle as ended using the cycle manager
        self.program_id.get_manager(constants.MANAGER_CYCLE).mark_ended(self)

    def mark_cancelled(self):
        # 1. Mark the cycle as cancelled using the cycle manager
        self.program_id.get_manager(constants.MANAGER_CYCLE).mark_cancelled(self)

    def validate_entitlement(self):
        # 1. Make sure the user has the right to do this
        # 2. Validate the entitlement of the beneficiaries using entitlement_manager.validate_entitlements()
        pass

    def export_distribution_list(self):
        # Not sure if this should be here.
        # It could be customizable reports based on https://github.com/OCA/reporting-engine
        pass

    def duplicate(self, new_start_date):
        # 1. Make sure the user has the right to do this
        # 2. Copy the cycle using the cycle manager
        pass

    def open_cycle_form(self):
        return {
            "name": "Cycle",
            "view_mode": "form",
            "res_model": "g2p.cycle",
            "res_id": self.id,
            "view_id": self.env.ref("g2p_programs.view_cycle_form").id,
            "type": "ir.actions.act_window",
            "target": "current",
            "flags": {"mode": "readonly"},
        }

    def open_members_form(self):
        self.ensure_one()

        action = {
            "name": _("Cycle Members"),
            "type": "ir.actions.act_window",
            "res_model": "g2p.cycle.membership",
            "context": {
                "create": False,
                "default_cycle_id": self.id,
                "search_default_enrolled_state": 1,
            },
            "view_mode": "list,form",
            "domain": [("cycle_id", "=", self.id)],
        }
        return action

    def open_entitlements_form(self):
        self.ensure_one()

        action = {
            "name": _("Cycle Entitlements"),
            "type": "ir.actions.act_window",
            "res_model": "g2p.entitlement",
            "context": {
                "create": False,
                "default_cycle_id": self.id,
                # "search_default_approved_state": 1,
            },
            "view_mode": "list,form",
            "domain": [("cycle_id", "=", self.id)],
        }
        return action
