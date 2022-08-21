# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, api, fields, models

from . import constants

_logger = logging.getLogger(__name__)


class G2PProgram(models.Model):
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _name = "g2p.program"
    _description = "Program"
    _order = "id desc"
    _check_company_auto = True

    MANAGER_ELIGIBILITY = constants.MANAGER_ELIGIBILITY
    MANAGER_CYCLE = constants.MANAGER_CYCLE
    MANAGER_PROGRAM = constants.MANAGER_PROGRAM
    MANAGER_ENTITLEMENT = constants.MANAGER_ENTITLEMENT
    MANAGER_DEDUPLICATION = constants.MANAGER_DEDUPLICATION
    MANAGER_NOTIFICATION = constants.MANAGER_NOTIFICATION

    MANAGER_MODELS = constants.MANAGER_MODELS

    # TODO: Associate a Wallet to each program using the accounting module
    # TODO: (For later) Associate a Warehouse to each program using the stock module for in-kind programs

    @api.model
    def _default_journal_id(self):
        journals = self.env["account.journal"].search(
            [("beneficiary_disb", "=", True), ("type", "in", ("bank", "cash"))]
        )
        if journals:
            return journals[0].id
        else:
            return None

    name = fields.Char(required=True)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    target_type = fields.Selection(
        selection=[("group", "Group"), ("individual", "Individual")], default="group"
    )

    # delivery_mechanism = fields.Selection([("mobile", "Mobile"), ("bank_account", "Bank Account"),
    # ("id", "ID Document"), ("biometric", "Biometrics")], default='id')

    # Pre-cycle steps
    # TODO: for those, we should allow to have multiple managers and
    #  the order of the steps should be defined by the user
    eligibility_managers = fields.Many2many(
        "g2p.eligibility.manager", string="Eligibility Managers"
    )  # All will be run
    deduplication_managers = fields.Many2many(
        "g2p.deduplication.manager", string="Deduplication Managers"
    )  # All will be run
    # for each beneficiary, their preferred will be used or the first one that works.
    notification_managers = fields.Many2many(
        "g2p.program.notification.manager", string="Notification Managers"
    )
    program_managers = fields.Many2many(
        "g2p.program.manager", string="Program Managers"
    )
    # Cycle steps
    cycle_managers = fields.Many2many("g2p.cycle.manager", string="Cycle Managers")
    entitlement_managers = fields.Many2many(
        "g2p.program.entitlement.manager", string="Entitlement Managers"
    )

    reconciliation_managers = fields.Selection([])

    program_membership_ids = fields.One2many(
        "g2p.program_membership", "program_id", "Program Memberships"
    )
    have_members = fields.Boolean(
        string="Have Beneficiaries",
        compute="_compute_have_members",
        default=False,
        store=True,
    )
    cycle_ids = fields.One2many("g2p.cycle", "program_id", "Cycles")

    date_ended = fields.Date("Date Ended")
    state = fields.Selection(
        [("active", "Active"), ("ended", "Ended")],
        "Status",
        default="active",
        readonly=True,
    )

    # Accounting config
    journal_id = fields.Many2one(
        "account.journal",
        "Disbursement Journal",
        domain=[("beneficiary_disb", "=", True), ("type", "in", ("bank", "cash"))],
        default=_default_journal_id,
    )

    # Statistics
    eligible_beneficiaries_count = fields.Integer(
        string="# Eligible Beneficiaries", compute="_compute_eligible_beneficiary_count"
    )
    beneficiaries_count = fields.Integer(
        string="# Beneficiaries", compute="_compute_beneficiary_count"
    )

    cycles_count = fields.Integer(string="# Cycles", compute="_compute_cycle_count")
    duplicate_membership_count = fields.Integer(
        string="# Membership Duplicates", compute="_compute_duplicate_membership_count"
    )
    active = fields.Boolean(default=True)

    @api.depends("program_membership_ids")
    def _compute_have_members(self):
        if len(self.program_membership_ids) > 0:
            self.have_members = True

    @api.model
    def create(self, vals):
        res = super(G2PProgram, self).create(vals)
        program_id = res.id
        man_ids = self.create_default_managers(program_id)
        for man in man_ids:
            res.update({man: [(4, man_ids[man])]})
        return res

    @api.model
    def create_default_managers(self, program_id):
        ret_vals = {}
        for mgr_fld in self.MANAGER_MODELS:
            for mgr_obj in self.MANAGER_MODELS[mgr_fld]:
                # Add a new record to default manager models
                def_mgr_obj = self.MANAGER_MODELS[mgr_fld][mgr_obj]
                _logger.info("DEBUG: %s" % def_mgr_obj)
                def_mgr = self.env[def_mgr_obj].create(
                    {
                        "name": "Default",
                        "program_id": program_id,
                    }
                )
                # Add a new record to manager parent models
                man_obj = self.env[mgr_obj]
                mgr = man_obj.create(
                    {
                        "program_id": program_id,
                        "manager_ref_id": "%s,%s" % (def_mgr_obj, str(def_mgr.id)),
                    }
                )
                ret_vals.update({mgr_fld: mgr.id})
        return ret_vals

    @api.depends("program_membership_ids")
    def _compute_duplicate_membership_count(self):
        for rec in self:
            duplicate_membership_count = 0
            if rec.program_membership_ids:
                duplicate_membership_count = len(
                    rec.program_membership_ids.filtered(
                        lambda bn: bn.state == "duplicated"
                    )
                )
            rec.update({"duplicate_membership_count": duplicate_membership_count})

    @api.depends("program_membership_ids")
    def _compute_eligible_beneficiary_count(self):
        for rec in self:
            eligible_beneficiaries_count = 0
            if rec.program_membership_ids:
                eligible_beneficiaries_count = len(
                    rec.program_membership_ids.filtered(
                        lambda bn: bn.state == "enrolled"
                    )
                )
            rec.update({"eligible_beneficiaries_count": eligible_beneficiaries_count})

    @api.depends("program_membership_ids")
    def _compute_beneficiary_count(self):
        for rec in self:
            rec.update({"beneficiaries_count": len(rec.program_membership_ids)})

    @api.depends("cycle_ids")
    def _compute_cycle_count(self):
        for rec in self:
            cycles_count = 0
            if rec.cycle_ids:
                cycles_count = len(rec.cycle_ids)
            rec.update({"cycles_count": cycles_count})

    @api.model
    def get_manager(self, kind):
        self.ensure_one()
        for rec in self:
            if kind == self.MANAGER_CYCLE:
                managers = rec.cycle_managers
            elif kind == self.MANAGER_PROGRAM:
                managers = rec.program_managers
            elif kind == self.MANAGER_ENTITLEMENT:
                managers = rec.entitlement_managers
            else:
                raise NotImplementedError("Manager not supported")
            if managers:
                managers.ensure_one()
                for el in managers:
                    return el.manager_ref_id

    @api.model
    def get_managers(self, kind):
        self.ensure_one()
        for rec in self:
            if kind == self.MANAGER_ELIGIBILITY:
                managers = rec.eligibility_managers
            elif kind == self.MANAGER_DEDUPLICATION:
                managers = rec.deduplication_managers
            elif kind == self.MANAGER_NOTIFICATION:
                managers = rec.notification_managers
            else:
                raise NotImplementedError("Manager not supported")
            return [el.manager_ref_id for el in managers]

    @api.model
    def get_beneficiaries(self, state):
        if isinstance(state, str):
            state = [state]
        for rec in self:
            domain = [("state", "in", state), ("program_id", "=", rec.id)]
            return self.env["g2p.program_membership"].search(domain)

    # TODO: JJ - Review
    def count_beneficiaries(self, state=None):

        domain = []
        if state is not None:
            domain = [("state", "in", state)]

        return {"value": self.env["g2p.program_membership"].search_count(domain)}

    # TODO: JJ - Add a way to link reports/Dashboard about this program.

    def enroll_eligible_registrants(self):
        # TODO: JJ - Think about how can we make it asynchronous.
        for rec in self:
            members = rec.get_beneficiaries(state=["draft"])
            _logger.info("members: %s", members)
            eligibility_managers = rec.get_managers(self.MANAGER_ELIGIBILITY)
            if len(eligibility_managers):
                for el in eligibility_managers:
                    members = el.enroll_eligible_registrants(members)
                # list the one not already enrolled:
                _logger.info("members filtered: %s", members)
                not_enrolled = members.filtered(lambda m: m.state != "enrolled")
                _logger.info("not_enrolled: %s", not_enrolled)
                not_enrolled.write(
                    {
                        "state": "enrolled",
                        "enrollment_date": fields.Datetime.now(),
                    }
                )
                if len(not_enrolled) > 0:
                    message = _("%s Beneficiaries enrolled." % len(not_enrolled))
                    kind = "success"
                else:
                    message = _("No Beneficiaries enrolled.")
                    kind = "warning"
            else:
                message = _("No Eligibility Manager defined.")
                kind = "danger"

            if kind == "success":
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Enrollment"),
                        "message": message + " %s",
                        "links": [
                            {
                                "label": "Refresh Page",
                            }
                        ],
                        "sticky": True,
                        "type": kind,
                    },
                }
            else:
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Enrollment"),
                        "message": message,
                        "sticky": True,
                        "type": kind,
                    },
                }

    def deduplicate_beneficiaries(self):
        for rec in self:
            deduplication_managers = rec.get_managers(self.MANAGER_DEDUPLICATION)
            message = None
            kind = "success"
            if len(deduplication_managers):
                states = ["draft", "enrolled", "eligible", "paused", "duplicated"]
                duplicates = 0
                for el in deduplication_managers:
                    duplicates += el.deduplicate_beneficiaries(states)

                if duplicates > 0:
                    message = _("%s Beneficiaries duplicate." % duplicates)
                    kind = "warning"
            else:
                message = _("No Deduplication Manager defined.")
                kind = "danger"

            if message:
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Deduplication"),
                        "message": message,
                        "sticky": True,
                        "type": kind,
                    },
                }

    def notify_eligible_beneficiaries(self):
        # 1. Notify the beneficiaries using notification_manager.enrolled_in_program()
        pass

    def create_new_cycle(self):
        # 1. Create the next cycle using cycles_manager.new_cycle()
        # 2. Import the beneficiaries from the previous cycle to this one. If it is the first one, import from the
        # program memberships.
        for rec in self:
            message = None
            kind = "success"
            cycle_manager = rec.get_manager(self.MANAGER_CYCLE)
            program_manager = rec.get_manager(self.MANAGER_PROGRAM)
            if cycle_manager is None:
                message = _("No Eligibility Manager defined.")
                kind = "danger"
            elif program_manager is None:
                message = _("No Program Manager defined.")
                kind = "danger"
            if message is not None:
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

            _logger.info("-" * 80)
            _logger.info("pm: %s", program_manager)
            new_cycle = program_manager.new_cycle()
            message = _("New cycle %s created." % new_cycle.name)
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Cycle"),
                    "message": message + " %s",
                    "links": [
                        {
                            "label": "Refresh Page",
                        }
                    ],
                    "sticky": True,
                    "type": kind,
                },
            }

    def create_journal(self):
        for rec in self:
            program_name = rec.name.split(" ")
            code = ""
            for pn in program_name:
                if pn:
                    code += pn[0].upper()
            if len(code) == 0:
                code = program_name[3].strip().upper()
            account_chart = self.env["account.account"].search(
                [
                    ("company_id", "=", self.env.company.id),
                    ("user_type_id.type", "=", "liquidity"),
                ]
            )
            default_account_id = None
            if account_chart:
                default_account_id = account_chart[0].id
            new_journal = self.env["account.journal"].create(
                {
                    "name": rec.name,
                    "beneficiary_disb": True,
                    "type": "bank",
                    "default_account_id": default_account_id,
                    "code": code,
                    "currency_id": rec.company_id.currency_id
                    and rec.company_id.currency_id.id
                    or None,
                }
            )
            rec.update({"journal_id": new_journal.id})

    def end_program(self):
        for rec in self.env.context.get("active_ids"):
            program = self.env["g2p.program"].search(
                [
                    ("id", "=", rec),
                ]
            )
            if program.state == "active":
                program.update({"state": "ended", "date_ended": fields.Date.today()})
            else:
                message = _("Ony 'active' programs can be ended.")
                kind = "danger"

                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Program"),
                        "message": message,
                        "sticky": True,
                        "type": kind,
                    },
                }

    def reactivate_program(self):
        for rec in self.env.context.get("active_ids"):
            program = self.env["g2p.program"].search(
                [
                    ("id", "=", rec),
                ]
            )
            if program.state == "ended":
                program.update({"state": "active", "date_ended": None})
            else:
                message = _("Ony 'ended' programs can be re-activated.")
                kind = "danger"

                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Project"),
                        "message": message,
                        "sticky": True,
                        "type": kind,
                    },
                }

    def open_eligible_beneficiaries_form(self):
        self.ensure_one()

        action = {
            "name": _("Beneficiaries"),
            "type": "ir.actions.act_window",
            "res_model": "g2p.program_membership",
            "context": {
                "create": False,
                "default_program_id": self.id,
                # "search_default_enrolled_state": 1,
            },
            "view_mode": "list,form",
            "domain": [("program_id", "=", self.id)],
        }
        return action

    def open_duplicate_membership_form(self):
        self.ensure_one()

        action = {
            "name": _("Beneficiaries Duplicates"),
            "type": "ir.actions.act_window",
            "res_model": "g2p.program_membership",
            "context": {
                "create": False,
                "default_program_id": self.id,
                # "search_default_enrolled_state": 1,
            },
            "view_mode": "list,form",
            "domain": [("program_id", "=", self.id), ("state", "=", "duplicated")],
        }
        return action

    def open_cycles_form(self):
        self.ensure_one()

        action = {
            "name": _("Cycles"),
            "type": "ir.actions.act_window",
            "res_model": "g2p.cycle",
            "context": {
                "create": False,
                "default_program_id": self.id,
                # "search_default_approved_state": 1,
                # "search_default_to_approve_state": 1,
            },
            "view_mode": "list,form",
            "domain": [("program_id", "=", self.id)],
        }
        return action
