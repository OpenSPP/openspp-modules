from odoo import fields, models


class EventDataAgriProdSalesCostTechDuringColdDrySeasonCropsProduced(models.Model):
    _name = "spp.event.agri.prod.sales.cost.tech.ds.prod"
    _description = "Agricultural Production, Sales, Cost and Technologies During Cold DS (Crops Produced)"

    agri_prod_sales_cost_tech_ids = fields.One2many(
        "spp.event.agri.prod.sales.cost.tech.ds.prod.lines",
        "agri_prod_sales_cost_tech_id",
        string="Agricultural Production, Sales, Cost and Technologies During Cold DS (Crops Produced)",
    )


class EventDataAgriProdSalesCostTechDuringColdDrySeasonCropsProducedLines(models.Model):
    _name = "spp.event.agri.prod.sales.cost.tech.ds.prod.lines"
    _description = "Agricultural Production, Sales, Cost and Technologies During Cold DS Lines (Crops Produced)"

    agri_prod_sales_cost_tech_id = fields.Many2one(
        "spp.event.agri.prod.sales.cost.tech.ds.prod",
        string="Agricultural Production, Sales, Cost and Technologies during Cold DS (Crops Produced)",
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
    harvest_area = fields.Float("Harvest Area (ha)")
    harvest_amt_kg = fields.Float("Harvest Amount (kg)")
    sales_qty_kg = fields.Float("Sales Quantity (kg)")
    sales_price_lak_kg = fields.Float("Sales Price (LAK/kg)")
    sales_value = fields.Float("Sales Value")
    contract_farming = fields.Selection([("1", "Yes"), ("2", "No")])
    partner_name = fields.Char("Name of partner in contact farming")
