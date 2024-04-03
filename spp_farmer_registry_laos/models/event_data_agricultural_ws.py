from odoo import api, fields, models


class OpenSPPEventDataAgriculturalWS(models.Model):
    _name = "spp.event.agri.ws"
    _description = "VIII. Agricultural Production, Sales, Costs and Technologies During the WS 2022 (cont)"

    agri_ws_produce_ids = fields.One2many("spp.event.agri.ws.produce", "agri_ws_id", string="Crops produce")
    agri_ws_cost_ids = fields.One2many("spp.event.agri.ws.cost", "agri_ws_id", string="Production cost per crop")
    experience_dryspell_flood = fields.Integer("Experience any dry spell / "
                                               "flood / hailstorm / storm during the WS 2022 cropping season")
    experience_dryspell_flood_dates = fields.Char("If yes, when?")
    experience_pest_disease_outbreak = fields.Integer("Experience any pest or disease outbreak "
                                                      "on your farmland during the WS 2022 cropping season")
    experience_pest_disease_outbreak_dates = fields.Char("If yes, when?")
    experience_pest_disease_outbreak_type = fields.Char("Type of pest or disease")
    experience_pest_disease_outbreak_affected = fields.Char("Affected crops (crop's code)")

    def get_view_id(self):
        """
        This retrieves the View ID of this model
        """
        return self.env["ir.ui.view"].search([("model", "=", self._name), ("type", "=", "form")], limit=1).id


class OpenSPPEventDataAgriculturalWSProduce(models.Model):
    _name = "spp.event.agri.ws.produce"
    _description = "Agricultural Production"

    agri_ws_id = fields.Many2one("spp.event.agri.ws")
    crop = fields.Many2one("spp.farm.species", domain="[('species_type', '=', 'crop')]")
    cropping_period_sowing = fields.Char("Cropping Period: Sowing")
    cropping_period_harvest = fields.Char("Cropping Period: Harvest")
    harvest_area = fields.Float("Harvest area -ha (a)")
    harvest_amount = fields.Float("Harvest amount -kg (b)")
    harvest_share = fields.Integer("Share of harvested produce")
    sales_qty = fields.Float("Sales qty -kg (c)")
    sales_price = fields.Float("Sales price LAK/kg (d)")
    sales_value = fields.Float("Sales value (e)=(c)x(d)")
    contract_farming = fields.Integer()
    name_of_partner = fields.Char()


class OpenSPPEventDataAgriculturalWSCost(models.Model):
    _name = "spp.event.agri.ws.cost"
    _description = "Product cost per crop"

    agri_ws_id = fields.Many2one("spp.event.agri.ws")
    crop_id = fields.Many2one("spp.farm.species", string="Crop", domain="[('species_type', '=', 'crop')]")
    labor_input = fields.Integer("Labor Input (days)")
    preparation_farmland = fields.Integer("Preparation of Farmland")
    seeds = fields.Integer("Preparation of Farmland")
    labor_cost = fields.Integer()
    fertilizer = fields.Integer()
    pesticide = fields.Integer()
    herbicide = fields.Integer("Herbicide and other agro-chem")
    water_fee = fields.Integer()
    tool_equipment = fields.Integer()
    other_fees = fields.Integer()
    total_production = fields.Integer("Total Production Cost")
