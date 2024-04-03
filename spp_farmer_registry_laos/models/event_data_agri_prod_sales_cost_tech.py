from odoo import fields, models


class EventDataAgriProdSalesCostTech(models.Model):
    _name = "spp.event.agri.prod.sales.cost.tech"
    _description = "Agricultural Production, Sales, Cost and Technologies"

    agri_prod_sales_cost_tech_ids = fields.One2many(
        "spp.event.agri.prod.sales.cost.tech.lines",
        "agri_prod_sales_cost_tech_id",
        string="Agricultural Production, Sales, Cost and Technologies",
    )


class EventDataAgriProdSalesCostTechLines(models.Model):
    _name = "spp.event.agri.prod.sales.cost.tech.lines"
    _description = "Agricultural Production, Sales, Cost and Technologies Lines"

    agri_prod_sales_cost_tech_id = fields.Many2one(
        "spp.event.agri.prod.sales.cost.tech", string="Agricultural Production, Sales, Cost and Technologies"
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
    org_felt_pest_herb = fields.Selection(
        [("1", "Selected"), ("0", "Not Selected")], string="Organic Fertilizer, Pesticide / Herbicide"
    )
    greenhouse = fields.Selection([("1", "Selected"), ("0", "Not Selected")], string="Greenhouse")
    multing = fields.Selection([("1", "Selected"), ("0", "Not Selected")], string="Multing")
    irrigation_normal = fields.Selection([("1", "Selected"), ("0", "Not Selected")], string="Irrigation (Normal)")
    water_pump = fields.Selection([("1", "Selected"), ("0", "Not Selected")], string="Water Pump")
    drip_irrigation = fields.Selection([("1", "Selected"), ("0", "Not Selected")], string="Drip Irrigation")
    sprinkler = fields.Selection([("1", "Selected"), ("0", "Not Selected")], string="Sprinkler")
    machine_harvest = fields.Selection([("1", "Selected"), ("0", "Not Selected")], string="Machine Harvest")
    dry_processing = fields.Selection([("1", "Selected"), ("0", "Not Selected")], string="Dry Processing")
    post_harvest_treatment = fields.Selection(
        [("1", "Selected"), ("0", "Not Selected")], string="Post Harvest Treatment (Fungicide"
    )
    other = fields.Char("Others")
