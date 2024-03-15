from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    ticket_ids = fields.One2many("spp.ticket", "partner_id", string="Tickets")
    ticket_count = fields.Integer(string="Ticket Count", compute="_compute_ticket_count")

    @api.depends("ticket_ids")
    def _compute_ticket_count(self):
        for record in self:
            record.ticket_count = len(record.ticket_ids)
