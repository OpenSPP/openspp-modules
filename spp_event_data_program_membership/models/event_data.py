import json

from odoo import api, fields, models


class OpenSPPEventData(models.Model):
    _inherit = "spp.event.data"

    program_membership_id = fields.Many2one("g2p.program_membership")
    program_membership_id_domain = fields.Char(compute="_compute_program_membership_id_domain")

    @api.depends("partner_id")
    def _compute_program_membership_id_domain(self):
        for rec in self:
            domain = [("id", "=", 0)]
            if rec.partner_id:
                domain = [("partner_id", "=", rec.partner_id.id)]
            rec.program_membership_id_domain = json.dumps(domain)
