from odoo import fields, models


class OpenSPPEventDataLivestockFarming(models.Model):
    _name = "spp.event.livestock.farming"
    _description = "XII. Livestock Farming"

    survey_sched = fields.Selection(
        [("1", "Baseline"), ("2", "Midline"), ("3", "Endline")],
        string="Survey Schedule",
    )
    livestock_cost_ids = fields.One2many(
        "spp.event.livestock.farming.cost",
        "livestock_farming_id",
        string="Livestock Farming (Production Cost)",
    )
    livestock_tech_ids = fields.One2many(
        "spp.event.livestock.farming.tech",
        "livestock_farming_id",
        string="Livestock Farming (Technologies)",
    )

    def get_view_id(self):
        """
        This retrieves the View ID of this model
        """
        return self.env["ir.ui.view"].search([("model", "=", self._name), ("type", "=", "form")], limit=1).id


class OpenSPPEventDataLivestockFarmingCost(models.Model):
    _name = "spp.event.livestock.farming.cost"
    _description = "XII. Livestock Farming (Production Cost and Gross/Net Income)"

    livestock_farming_id = fields.Many2one(
        "spp.event.livestock.farming",
        string="Livestock Farming",
    )
    livestock_id = fields.Many2one(
        "spp.farm.species", string="Livestock", domain="[('species_type', '=', 'livestock')]"
    )
    labor_input_days = fields.Integer("Labor Input (Days)")
    purchase_baby_animal = fields.Float("Purchase of Baby Animals")
    feed = fields.Float()
    medicine = fields.Float()
    electricity_water = fields.Float("Electricity/Water Fees")
    facility_machinery = fields.Float("Facility/Machinery Equipment")
    labor_cost = fields.Float()
    oth_fees = fields.Float("Other Fees")
    oth_specify = fields.Char("Specify Other")
    total_cost = fields.Float("Total Cost (a)")
    farmgate_price = fields.Float()
    gross_income = fields.Float("Gross Income from the Sales (b)")
    net_income = fields.Float("Net Income (c)=(b)-(a)", compute="_compute_net_income")
    nb_head = fields.Integer("Nb. Head")

    def _compute_net_income(self):
        for rec in self:
            net_income = rec.gross_income - rec.total_cost
            rec.net_income = net_income


class OpenSPPEventDataLivestockFarmingTech(models.Model):
    _name = "spp.event.livestock.farming.tech"
    _description = "XII. Livestock Farming (Technologies/Techniques)"

    livestock_farming_id = fields.Many2one(
        "spp.event.livestock.farming",
        string="Livestock Farming",
    )
    livestock_id = fields.Many2one(
        "spp.farm.species", string="Livestock", domain="[('species_type', '=', 'livestock')]"
    )
    organic_fertilizer = fields.Selection(
        [("1", "Selected"), ("0", "Not Selected")], string="Organic Fertilizer, Pesticide / Herbicide"
    )
    hybrid_species = fields.Selection([("1", "Selected"), ("0", "Not Selected")])
    concentrated_feed = fields.Selection([("1", "Selected"), ("0", "Not Selected")])
    grass_planting_forage = fields.Selection([("1", "Selected"), ("0", "Not Selected")])
    vaccination = fields.Selection([("1", "Selected"), ("0", "Not Selected")])
    antibiotics = fields.Selection([("1", "Selected"), ("0", "Not Selected")])
    growth_hormone = fields.Selection([("1", "Selected"), ("0", "Not Selected")])
    other_disinfect = fields.Selection(
        [("1", "Selected"), ("0", "Not Selected")], string="Other disinfection and epidemic"
    )
    shed_livestock = fields.Selection([("1", "Selected"), ("0", "Not Selected")], string="Shed for Livestock")
    other = fields.Char("Others")
