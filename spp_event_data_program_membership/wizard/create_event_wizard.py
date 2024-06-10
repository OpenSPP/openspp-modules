import json

from odoo import api, fields, models


class SPPCreateEventWizard(models.TransientModel):
    _inherit = "spp.create.event.wizard"

    program_membership_id = fields.Many2one("g2p.program_membership")
    program_membership_id_domain = fields.Char(compute="_compute_program_membership_id_domain")

    @api.depends("partner_id")
    def _compute_program_membership_id_domain(self):
        for rec in self:
            domain = [("id", "=", 0)]
            if rec.partner_id:
                domain = [("partner_id", "=", rec.partner_id.id)]
            rec.program_membership_id_domain = json.dumps(domain)

    def get_event_data_vals(self):
        """
        This returns the event data values
        :return: Event Data Values
        """
        vals = super().get_event_data_vals()
        vals.update({"program_membership_id": self.program_membership_id.id})
        return vals
