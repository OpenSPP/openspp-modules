# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import json

from odoo import _, api, fields, models


class InKindEntitlement(models.TransientModel):
    _name = "g2p.entitlement.inkind.report.wizard"
    _description = "In-kind Entitlement Report Wizard"

    cycle_id = fields.Many2one("g2p.cycle", string="Cycle")
    program_id = fields.Many2one("g2p.program", string="Program", required=True)

    cycle_id_domain = fields.Char(
        compute="_compute_cycle_id_domain",
        readonly=True,
        store=False,
    )

    @api.depends("program_id")
    def _compute_cycle_id_domain(self):
        for rec in self:
            domain = [("program_id", "=", rec.program_id.id)]
            rec.cycle_id_domain = json.dumps(domain)

    def generate_report(self):
        for rec in self:
            domain = [("program_id", "=", rec.program_id.id)]
            if rec.cycle_id:
                domain.append(("cycle_id", "=", rec.cycle_id.id))
            context = {
                "create": False,
                "edit": False,
                "delete": False,
            }
            tree_id = self.env.ref("spp_programs.view_entitlement_inkind_report_tree").id
            form_id = self.env.ref("spp_programs.view_entitlement_inkind_form").id
            return {
                "name": _("In-kind Entitlement Report"),
                "view_mode": "tree",
                "res_model": "g2p.entitlement.inkind",
                "views": [(tree_id, "tree"), (form_id, "form")],
                "search_view_id": self.env.ref("spp_programs.action_entitlement_report_inkind").id,
                "domain": domain,
                "context": context,
                "type": "ir.actions.act_window",
                "target": "current",
                "flags": {"mode": "readonly"},
            }
