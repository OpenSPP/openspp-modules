from odoo import fields, models


class OpenSPPEventDataAgriculturalDS(models.Model):
    _name = "spp.event.agri.ds"
    _description = "X. Agricultural Production, Sales, Cost and Technologies During Cold DS"

    agri_prod_ids = fields.One2many(
        "spp.event.agri.ds.prod",
        "agri_ds_id",
        string="Agricultural Production During Cold DS",
    )
    agri_cost_ids = fields.One2many(
        "spp.event.agri.ds.cost",
        "agri_ds_id",
        string="Agricultural Cost During Cold DS",
    )
    agri_tech_ids = fields.One2many(
        "spp.event.agri.ds.tech",
        "agri_ds_id",
        string="Agricultural Technologies During Cold DS",
    )

    def get_view_id(self):
        """
        This retrieves the View ID of this model
        """
        return self.env["ir.ui.view"].search([("model", "=", self._name), ("type", "=", "form")], limit=1).id


class OpenSPPEventDataAgriculturalDSProduced(models.Model):
    _name = "spp.event.agri.ds.prod"
    _description = "X. Agricultural Production During Cold DS"

    agri_ds_id = fields.Many2one(
        "spp.event.agri.ds",
        string="Agricultural Production, Sales, Cost and Technologies during Cold DS",
    )
    crop_id = fields.Many2one("spp.farm.species", string="Crop", domain="[('species_type', '=', 'crop')]")
    harvest_area = fields.Float("Harvest Area (ha)")
    harvest_amt_kg = fields.Float("Harvest Amount (kg)")
    sales_qty_kg = fields.Float("Sales Quantity (kg)")
    sales_price_lak_kg = fields.Float("Sales Price (LAK/kg)")
    sales_value = fields.Float("Sales Value")
    contract_farming = fields.Selection([("1", "Yes"), ("2", "No")])
    partner_name = fields.Char("Name of partner in contact farming")


class OpenSPPEventDataAgriculturalDSCost(models.Model):
    _name = "spp.event.agri.ds.cost"
    _description = "X. Agricultural Cost During Cold DS"

    agri_ds_id = fields.Many2one(
        "spp.event.agri.ds",
        string="Agricultural Production, Sales, Cost and Technologies during Cold DS",
    )
    crop_id = fields.Many2one("spp.farm.species", string="Crop", domain="[('species_type', '=', 'crop')]")
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


class OpenSPPEventDataAgriculturalDSTech(models.Model):
    _name = "spp.event.agri.ds.tech"
    _description = "X. Agricultural Technologies During Cold DS"

    agri_ds_id = fields.Many2one(
        "spp.event.agri.ds",
        string="Agricultural Production, Sales, Cost and Technologies during Cold DS",
    )
    crop_id = fields.Many2one("spp.farm.species", string="Crop", domain="[('species_type', '=', 'crop')]")
    organic_fertilizer = fields.Selection(
        [("1", "Selected"), ("0", "Not Selected")], string="Organic Fertilizer, Pesticide / Herbicide"
    )
    greenhouse = fields.Selection([("1", "Selected"), ("0", "Not Selected")], string="Greenhouse")
    multing = fields.Selection([("1", "Selected"), ("0", "Not Selected")], string="Multying")
    irrigation = fields.Selection([("1", "Selected"), ("0", "Not Selected")], string="Irrigation (Normal)")
    water_pump = fields.Selection([("1", "Selected"), ("0", "Not Selected")], string="Water Pump")
    drip_irrigation = fields.Selection([("1", "Selected"), ("0", "Not Selected")], string="Drip Irrigation")
    sprinkler = fields.Selection([("1", "Selected"), ("0", "Not Selected")], string="Sprinkler")
    machine_harvest = fields.Selection([("1", "Selected"), ("0", "Not Selected")], string="Machine Harvest")
    dry_processing = fields.Selection([("1", "Selected"), ("0", "Not Selected")], string="Dry Processing")
    post_harvest_treatment = fields.Selection(
        [("1", "Selected"), ("0", "Not Selected")], string="Post Harvest Treatment (Fungicide)"
    )
    other = fields.Char("Others")
