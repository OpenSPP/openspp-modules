from odoo import fields, models


class EventDataAgriProdSalesCostTechDuringColdDrySeasonProductionCost(models.Model):
    _name = "spp.event.agri.prod.sales.cost.tech.ds.cost"
    _description = "Agricultural Production, Sales, Cost and Technologies During Cold DS (Production Cost)"

    agri_prod_sales_cost_tech_ids = fields.One2many(
        "spp.event.agri.prod.sales.cost.tech.ds.cost.lines",
        "agri_prod_sales_cost_tech_id",
        string="Agricultural Production, Sales, Cost and Technologies During Cold DS (Production Cost)",
    )


class EventDataAgriProdSalesCostTechDuringColdDrySeasonProductionCostLines(models.Model):
    _name = "spp.event.agri.prod.sales.cost.tech.ds.cost.lines"
    _description = "Agricultural Production, Sales, Cost and Technologies During Cold DS Lines (Production Cost)"

    agri_prod_sales_cost_tech_id = fields.Many2one(
        "spp.event.agri.prod.sales.cost.tech.ds.cost",
        string="Agricultural Production, Sales, Cost and Technologies during Cold DS (Production Cost)",
    )
    kind = fields.Selection(
        [
            ("1", "Rice"),
            ("2", "Black and Red Beans"),
            ("3", "Cantaloup (melon)"),
            ("4", "Corn (animal feed)"),
            ("5", "Corn (Human Consumption)"),
            ("6", "Cucumber"),
            ("7", "Peanuts"),
            ("8", "Potatoes"),
            ("9", "Pumpkin"),
            ("10", "Fruitbearing Vegetables"),
            ("11", "Gourd"),
            ("12", "Green Manure"),
            ("13", "Leafy Stem Vegetables"),
            ("14", "Long Beans"),
            ("15", "Mungbeans"),
            ("16", "Roots, Bulbs and Tuberous"),
            ("17", "Sesame"),
            ("18", "Soybean"),
            ("19", "Weet / Falang Beans"),
            ("20", "Sweet Potatoes"),
            ("21", "Tobacco"),
            ("22", "Watermelon"),
            ("23", "Winged Beans"),
            ("24", "Cassava"),
            ("25", "Sugarcane"),
            ("26", "Upland Rice"),
            ("27", "Job's Tear"),
            ("28", "Coffee"),
            ("29", "Tea"),
            ("30", "Tree Fruits"),
            ("31", "Cardamom"),
            ("32", "Ruber"),
            ("33", "Pine"),
            ("34", "Palm Tree"),
            ("35", "Teak"),
            ("36", "Other"),
        ],
        string="Crop Type",
    )
    labor_input_days = fields.Integer("Labor Input (Days)")
    preparation_farmland = fields.Float("Cost of Farmland Preparation")
    seeds = fields.Float("Cost of Seeds")
    labor_cost = fields.Float("Cost of Labor")
    fertilizer = fields.Float("Cost of Fertilizer")
    pesticide = fields.Float("Cost of Pesticide")
    herbicide_oth = fields.Float("Cost of Herbicide and Other Agro-chem")
    water_fee = fields.Float("Water Fee")
    total_equipment = fields.Float("Cost of Tools or Equipment")
    oth_fees = fields.Float("Other Fees")
    total_prod_cost = fields.Float("Total Production Cost")
