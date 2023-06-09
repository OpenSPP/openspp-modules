# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, api, fields, models
from odoo.osv.expression import AND, OR
from odoo.tools import safe_eval

# from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SPPCreateNewProgramWiz(models.TransientModel):
    _inherit = "g2p.program.create.wizard"

    @api.model
    def _get_admin_area_domain(self):
        return [("kind", "=", self.env.ref("spp_area.admin_area_kind").id)]

    admin_area_ids = fields.Many2many("spp.area", domain=_get_admin_area_domain)

    # SQL-base Eligibility Manager
    eligibility_kind = fields.Selection(
        [("default_eligibility", "Default")],
        "Eligibility Manager",
        default="default_eligibility",
    )

    @api.onchange("admin_area_ids")
    def on_admin_area_ids_change(self):
        eligibility_domain = self.eligibility_domain
        domain = []
        if eligibility_domain not in [None, "[]"]:
            # Do not remove other filters
            # Convert the string to list of tuples
            domain = safe_eval.safe_eval(eligibility_domain)
            # get the area_center_id from the list
            area_dom = [flt for flt in domain if "area_id" in flt]
            if area_dom:
                domain.remove(area_dom[0])

        if self.admin_area_ids:
            area_ids = self.admin_area_ids.ids
            domain.append(("area_id", "in", tuple(area_ids)))
        eligibility_domain = str(self._insert_domain_operator(domain))

        self.eligibility_domain = eligibility_domain

    def _insert_domain_operator(self, domain):
        """Insert operator to the domain"""
        if not domain:
            return domain
        operator_used = AND
        if domain[0] == "|":
            operator_used = OR
        new_domain = []
        domain = list(filter(lambda a: a not in ["&", "|", "!"], domain))
        for dom in domain:
            new_domain = operator_used([new_domain, [dom]])
        return new_domain

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
            vals.update(rec._get_eligibility_manager(program_id))

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
            def_mgr.update(self._get_recurrent_field_values())

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

            # Complete the program data
            program.update(vals)

            if rec.import_beneficiaries == "yes":
                eligibility_managers = program.get_managers(program.MANAGER_ELIGIBILITY)
                eligibility_managers[0].import_eligible_registrants(state="enrolled")

            # Open the newly created program
            action = {
                "name": _("Programs"),
                "type": "ir.actions.act_window",
                "res_model": "g2p.program",
                "view_mode": "form,list",
                "res_id": program_id,
            }
            return action

    def _get_eligibility_manager(self, program_id):
        val = None
        if self.eligibility_kind == "default_eligibility":
            # Add a new record to default eligibility manager model
            def_mgr_obj = "g2p.program_membership.manager.default"
            def_mgr = self.env[def_mgr_obj].create(
                {
                    "name": "Default",
                    "program_id": program_id,
                    "admin_area_ids": self.admin_area_ids,
                    "eligibility_domain": self.eligibility_domain,
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
            val = {"eligibility_managers": [(4, mgr.id)]}
        return val
