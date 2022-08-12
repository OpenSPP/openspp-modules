# Part of Newlogic G2P. See LICENSE file for full copyright and licensing details.
import logging
from uuid import uuid4

from odoo import _, api, fields, models
from odoo.exceptions import UserError

# from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class G2PCreateNewProgramWiz(models.TransientModel):
    _name = "g2p.program.create.wizard"
    _inherit = "base.programs.manager"
    _description = "Create a New Program Wizard"

    @api.model
    def default_get(self, fields):
        _logger.info("Creating a new program")
        res = super(G2PCreateNewProgramWiz, self).default_get(fields)

        _logger.info("DEBUG: active_model: %s" % self.env.context.get("active_model"))

        # Set default currency from the user's current company
        currency_id = (
            self.env.user.company_id.currency_id
            and self.env.user.company_id.currency_id.id
            or None
        )
        res["currency_id"] = currency_id
        return res

    name = fields.Char("Program Name", required=True)
    currency_id = fields.Many2one("res.currency", "Currency", required=True)

    # Eligibility Manager
    eligibility_domain = fields.Text(string="Domain", default="[]", required=True)

    # Cycle Manager
    auto_approve_entitlements = fields.Boolean(
        string="Auto-approve Entitlements", default=False
    )
    cycle_duration = fields.Integer("Cycle Duration", default=30, required=True)
    approver_group_id = fields.Many2one(
        comodel_name="res.groups",
        string="Approver Group",
    )

    # Entitlement Manager
    amount_per_cycle = fields.Monetary(
        currency_field="currency_id",
        group_operator="sum",
        default=0.0,
        string="Amount per cycle",
    )
    amount_per_individual_in_group = fields.Monetary(
        currency_field="currency_id",
        group_operator="sum",
        default=0.0,
        string="Amount per individual in group",
    )
    max_individual_in_group = fields.Integer(
        default=0,
        string="Maximum number of individual in group",
        help="0 means no limit",
    )
    entitlement_kind = fields.Selection(
        [("default", "Default")],
        "Applied For",
        default="default",
    )
    entitlement_validation_group_id = fields.Many2one(
        "res.groups", string="Entitlement Validation Group"
    )

    target_type = fields.Selection(
        [("group", "Group"), ("individual", "Individual")],
        "Target Type",
        default="group",
    )
    gen_benificiaries = fields.Selection(
        [("yes", "Yes"), ("no", "No")], "Generate Beneficiaries", default="no"
    )

    state = fields.Selection(
        [("step1", "Set Defaults"), ("step2", "Import Registrants")],
        "Status",
        default="step1",
        readonly=True,
    )

    def next_step(self):
        if self.state == "step1":
            self.state = "step2"
        return self._reopen_self()

    def prev_step(self):
        if self.state == "step2":
            self.state = "step1"
        return self._reopen_self()

    def _reopen_self(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def _check_required_fields(self):
        if (
            self.entitlement_kind == "default"
            and self.amount_per_cycle == 0.0
            and self.amount_per_individual_in_group == 0.0
        ):
            raise UserError(
                _(
                    "The 'Amount per cycle' or 'Amount per individual in group' "
                    + "must be filled-up for the default entitlement manager."
                )
            )

    def _get_entitlement_manager(self, program_id):
        val = None
        if self.entitlement_kind == "default":
            # Add a new record to default entitlement manager model
            def_mgr_obj = "g2p.program.entitlement.manager.default"
            def_mgr = self.env[def_mgr_obj].create(
                {
                    "name": "Default",
                    "program_id": program_id,
                    "amount_per_cycle": self.amount_per_cycle,
                    "amount_per_individual_in_group": self.amount_per_individual_in_group,
                    "max_individual_in_group": self.max_individual_in_group,
                    "entitlement_validation_group_id": self.entitlement_validation_group_id.id,
                }
            )
            # Add a new record to entitlement manager parent model
            man_obj = self.env["g2p.program.entitlement.manager"]
            mgr = man_obj.create(
                {
                    "program_id": program_id,
                    "manager_ref_id": "%s,%s" % (def_mgr_obj, str(def_mgr.id)),
                }
            )
            val = {"entitlement_managers": [(4, mgr.id)]}
        return val

    def create_program(self):
        self._check_required_fields()
        for rec in self:
            # Create a new journal for this program
            journal_id = self.create_journal(rec.name, rec.currency_id.id)

            program = self.env["g2p.program"].create(
                {
                    "name": rec.name,
                    "journal_id": journal_id,
                    "target_type": rec.target_type,
                }
            )
            program_id = program.id
            vals = {}

            # Set Default Eligibility Manager settings
            # Add a new record to default eligibility manager model
            def_mgr_obj = "g2p.program_membership.manager.default"
            def_mgr = self.env[def_mgr_obj].create(
                {
                    "name": "Default",
                    "program_id": program_id,
                    "eligibility_domain": rec.eligibility_domain,
                }
            )
            # Add a new record to eligibility manager parent model
            man_obj = self.env["g2p.eligibility.manager"]
            mgr = man_obj.create(
                {
                    "program_id": program_id,
                    "manager_ref_id": "%s,%s" % (def_mgr_obj, str(def_mgr.id)),
                }
            )
            vals.update({"eligibility_managers": [(4, mgr.id)]})

            # Set Default Cycle Manager settings
            # Add a new record to default cycle manager model
            def_mgr_obj = "g2p.cycle.manager.default"
            def_mgr = self.env[def_mgr_obj].create(
                {
                    "name": "Default",
                    "program_id": program_id,
                    "auto_approve_entitlements": rec.auto_approve_entitlements,
                    "cycle_duration": rec.cycle_duration,
                    "approver_group_id": rec.approver_group_id.id or None,
                }
            )
            # Add a new record to cycle manager parent model
            man_obj = self.env["g2p.cycle.manager"]
            mgr = man_obj.create(
                {
                    "program_id": program_id,
                    "manager_ref_id": "%s,%s" % (def_mgr_obj, str(def_mgr.id)),
                }
            )
            vals.update({"cycle_managers": [(4, mgr.id)]})

            # Set Default Entitlement Manager
            vals.update(rec._get_entitlement_manager(program_id))

            # Enroll beneficiaries
            if rec.gen_benificiaries == "yes":
                domain = [("is_registrant", "=", True)]
                if rec.target_type == "group":
                    domain += [("is_group", "=", True)]
                else:
                    domain += [("is_group", "=", False)]
                domain += self._safe_eval(rec.eligibility_domain)
                # Filter res.partner and get ids
                partners = self.env["res.partner"].search(domain)
                if partners:
                    partner_vals = []
                    for p in partners.ids:
                        partner_vals.append((0, 0, {"partner_id": p}))
                    vals.update({"program_membership_ids": partner_vals})
                    _logger.info("DEBUG: %s" % partner_vals)

            # Complete the program data
            program.update(vals)

            # Open the newly created program
            action = {
                "name": _("Programs"),
                "type": "ir.actions.act_window",
                "res_model": "g2p.program",
                "view_mode": "form,list",
                "res_id": program_id,
            }
            return action

    def close_wizard(self):
        return {"type": "ir.actions.act_window_close"}

    def create_journal(self, name, currency_id):
        program_name = name.split(" ")
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
        # Check if code is unique
        code_exist = self.env["account.journal"].search([("code", "=", code)])
        if code_exist:
            # code += str(len(code_exist)) + code
            code = str(uuid4())[4:-19][1:]
        default_account_id = None
        if account_chart:
            default_account_id = account_chart[0].id
        new_journal = self.env["account.journal"].create(
            {
                "name": name,
                "beneficiary_disb": True,
                "type": "bank",
                "default_account_id": default_account_id,
                "code": code,
                "currency_id": currency_id,
            }
        )
        return new_journal.id
