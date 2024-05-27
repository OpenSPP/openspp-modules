from odoo import api, fields, models


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


class OpenSPPEventDataIncomeFromAgribusinessResPartner(models.Model):
    _inherit = "res.partner"

    active_event_inc_agri = fields.Many2one("spp.event.inc.agri", compute="_compute_active_event_inc_agri", store=True)

    xiii_survey_schedule = fields.Selection(string="Survey Schedule", related="active_event_inc_agri.survey_sched")
    xiii_sales_of_input = fields.Float("Income from Sales of Input", related="active_event_inc_agri.sales_of_input")
    xiii_sales_baby_animals = fields.Float(
        "Income from Sales of Baby Animals", related="active_event_inc_agri.sales_baby_animals"
    )
    xiii_sales_of_animal_feeds = fields.Float(
        "Income from Sales of Animal Feeds", related="active_event_inc_agri.sales_of_animal_feeds"
    )
    xiii_rental_agri_machinery = fields.Float(
        "Income from Rental of Agricultural Machinery", related="active_event_inc_agri.rental_agri_machinery"
    )
    xiii_processing_agro_products = fields.Float(
        "Income from Processing of Agro-Products", related="active_event_inc_agri.processing_agro_products"
    )
    xiii_transport_trade_agro_products = fields.Float(
        "Income from Transport and Trade of Agro-Products",
        related="active_event_inc_agri.transport_trade_agro_products",
    )
    xiii_other = fields.Float("Other Income from Agribusiness", related="active_event_inc_agri.other")

    @api.depends("event_data_ids")
    def _compute_active_event_inc_agri(self):
        """
        This computes the active Income from Agribusiness (LAK) event of the group
        """
        for rec in self:
            event_data = rec._get_active_event_id("spp.event.inc.agri")
            rec.active_event_inc_agri = None
            if event_data:
                event_data_res_id = self.env["spp.event.data"].search([("id", "=", event_data)], limit=1).res_id
                rec.active_event_inc_agri = (
                    self.env["spp.event.inc.agri"].search([("id", "=", event_data_res_id)], limit=1).id
                )
