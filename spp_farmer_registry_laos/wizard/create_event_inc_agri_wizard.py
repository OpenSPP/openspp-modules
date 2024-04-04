# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import Command, fields, models


class SPPCreateEventIncomeFromAgribusinessWizard(models.TransientModel):
    _name = "spp.create.event.inc.agri.wizard"
    _description = "XIII. Income from Agribusiness (LAK)"

    event_id = fields.Many2one("spp.event.data")

    sales_of_input = fields.Float("Income from Sales of Input")
    sales_baby_animals = fields.Float("Income from Sales of Baby Animals")
    sales_of_animal_feeds = fields.Float("Income from Sales of Animal Feeds")
    rental_agri_machinery = fields.Float("Income from Rental of Agricultural Machinery")
    processing_agro_products = fields.Float("Income from Processing of Agro-Products")
    transport_trade_agro_products = fields.Float("Income from Transport and Trade of Agro-Products")
    other = fields.Float("Other Income from Agribusiness")

    def create_event(self):
        for rec in self:
            vals_list = {
                "sales_of_input": rec.sales_of_input,
                "sales_baby_animals": rec.sales_baby_animals,
                "sales_of_animal_feeds": rec.sales_of_animal_feeds,
                "rental_agri_machinery": rec.rental_agri_machinery,
                "processing_agro_products": rec.processing_agro_products,
                "transport_trade_agro_products": rec.transport_trade_agro_products,
                "other": rec.other,
            }

            event = self.env["spp.event.inc.agri"].create(vals_list)
            rec.event_id.res_id = event.id

            return event
