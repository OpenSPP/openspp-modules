from odoo import fields, models


class OpenSPPEventDataIncomeFromAgribusiness(models.Model):
    _name = "spp.event.inc.agri"
    _description = "XIII. Income from Agribusiness (LAK)"

    survey_sched = fields.Selection(
        [("1", "Baseline"), ("2", "Midline"), ("3", "Endline")],
        string="Survey Schedule",
    )
    sales_of_input = fields.Float("Income from Sales of Input")
    sales_baby_animals = fields.Float("Income from Sales of Baby Animals")
    sales_of_animal_feeds = fields.Float("Income from Sales of Animal Feeds")
    rental_agri_machinery = fields.Float("Income from Rental of Agricultural Machinery")
    processing_agro_products = fields.Float("Income from Processing of Agro-Products")
    transport_trade_agro_products = fields.Float("Income from Transport and Trade of Agro-Products")
    other = fields.Float("Other Income from Agribusiness")

    def get_view_id(self):
        """
        This retrieves the View ID of this model
        """
        return self.env["ir.ui.view"].search([("model", "=", self._name), ("type", "=", "form")], limit=1).id
