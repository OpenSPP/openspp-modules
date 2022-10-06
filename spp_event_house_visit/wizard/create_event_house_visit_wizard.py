# Part of OpenG2P. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SPPCreateEventHouseVisitWizard(models.TransientModel):
    _name = "spp.create.event.house.visit.wizard"
    _description = "Create Event House Visit Wizard"

    registrant = fields.Many2one(
        "res.partner", domain=[("is_group", "=", True), ("is_registrant", "=", True)]
    )
    summary = fields.Char()
    description = fields.Text()

    def create_event(self):
        for rec in self:
            if rec.registrant.active_house_visit:
                rec.registrant.end_active_event(rec.registrant.active_house_visit)

            vals_list = [
                {
                    "registrant": rec.registrant.id,
                    "description": rec.description or False,
                    "summary": rec.summary or False,
                }
            ]
            self.env["spp.event.house.visit"].create(vals_list)
