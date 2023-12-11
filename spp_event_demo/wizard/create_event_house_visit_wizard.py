# Part of OpenG2P. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SPPCreateEventHouseVisitWizard(models.TransientModel):
    _name = "spp.create.event.house.visit.wizard"
    _description = "Create Event House Visit Wizard"

    event_id = fields.Many2one("spp.event.data")
    summary = fields.Char()
    is_farm = fields.Boolean(default=False)
    farm_size_acre = fields.Float()
    photo = fields.Binary()
    photo_filename = fields.Char()
    number_of_pigs = fields.Integer()
    number_of_cows = fields.Integer()
    no_food_stock = fields.Integer()
    disabled = fields.Boolean(default=False)

    def create_event(self):
        for rec in self:
            vals_list = [
                {
                    "summary": rec.summary or False,
                    "is_farm": rec.is_farm or False,
                    "farm_size_acre": rec.farm_size_acre or False,
                    "photo": rec.photo or False,
                    "photo_filename": rec.photo_filename or False,
                    "number_of_pigs": rec.number_of_pigs or False,
                    "number_of_cows": rec.number_of_cows or False,
                    "no_food_stock": rec.no_food_stock or False,
                    "disabled": rec.disabled or False,
                }
            ]
            event = self.env["spp.event.house.visit"].create(vals_list)
            rec.event_id.res_id = event.id

            return event
