# Part of OpenG2P. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SPPCreateEventHouseVisitWizard(models.TransientModel):
    _name = "spp.create.event.house.visit.wizard"
    _description = "Create Event House Visit Wizard"

    event_id = fields.Many2one("spp.event.data")
    summary = fields.Char()
    description = fields.Text()

    def create_event(self):
        for rec in self:
            vals_list = [
                {
                    "description": rec.description or False,
                    "summary": rec.summary or False,
                }
            ]
            event = self.env["spp.event.house.visit"].create(vals_list)
            rec.event_id.res_id = event.id

            return event
