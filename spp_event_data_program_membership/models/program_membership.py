from odoo import api, models


class G2PProgramMembership(models.Model):
    _inherit = "g2p.program_membership"

    @api.depends("program_id", "partner_id")
    def _compute_display_name(self):
        for rec in self:
            name = ""
            if rec.program_id:
                name += "[" + rec.program_id.name + "] "
            if rec.partner_id:
                name += rec.partner_id.name
            rec.display_name = name
