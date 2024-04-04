# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import Command, fields, models


class SPPCreateEventLivestockFarmingWizard(models.TransientModel):
    _name = "spp.create.event.livestock.farming.wizard"
    _description = "XII. Livestock Farming"

    event_id = fields.Many2one("spp.event.data")
    survey_sched = fields.Selection(
        [("1", "Baseline"), ("2", "Midline"), ("3", "Endline")],
        string="Survey Schedule",
    )
    livestock_cost_ids = fields.One2many(
        "spp.create.event.livestock.farming.cost.wizard",
        "livestock_farming_id",
        string="Livestock Farming (Production Cost)",
    )
    livestock_tech_ids = fields.One2many(
        "spp.create.event.livestock.farming.tech.wizard",
        "livestock_farming_id",
        string="Livestock Farming (Technologies)",
    )

    def create_event(self):
        for rec in self:
            vals_list = {"survey_sched": rec.survey_sched}

            if rec.livestock_cost_ids:
                cost_vals = []
                for cost in rec.livestock_cost_ids:
                    cost_vals.append(
                        Command.create(
                            {
                                "livestock_id": cost.livestock_id.id,
                                "labor_input_days": cost.labor_input_days,
                                "purchase_baby_animal": cost.purchase_baby_animal,
                                "feed": cost.feed,
                                "medicine": cost.medicine,
                                "electricity_water": cost.electricity_water,
                                "facility_machinery": cost.facility_machinery,
                                "labor_cost": cost.labor_cost,
                                "oth_fees": cost.oth_fees,
                                "oth_specify": cost.oth_specify,
                                "total_cost": cost.total_cost,
                                "farmgate_price": cost.farmgate_price,
                                "gross_income": cost.gross_income,
                                "nb_head": cost.nb_head,
                            }
                        )
                    )
                vals_list.update({"livestock_cost_ids": cost_vals})

            if rec.livestock_tech_ids:
                tech_vals = []
                for tech in rec.livestock_tech_ids:
                    tech_vals.append(
                        Command.create(
                            {
                                "livestock_id": tech.livestock_id.id,
                                "organic_fertilizer": tech.organic_fertilizer,
                                "hybrid_species": tech.hybrid_species,
                                "concentrated_feed": tech.concentrated_feed,
                                "grass_planting_forage": tech.grass_planting_forage,
                                "vaccination": tech.vaccination,
                                "antibiotics": tech.antibiotics,
                                "growth_hormone": tech.growth_hormone,
                                "other_disinfect": tech.other_disinfect,
                                "shed_livestock": tech.shed_livestock,
                                "other": tech.other,
                            }
                        )
                    )
                vals_list.update({"livestock_tech_ids": tech_vals})

            event = self.env["spp.event.livestock.farming"].create(vals_list)
            rec.event_id.res_id = event.id

            return event


class SPPCreateEventLivestockFarmingCostWizard(models.TransientModel):
    _name = "spp.create.event.livestock.farming.cost.wizard"
    _description = "XII. Livestock Farming (Production Cost and Gross/Net Income)"

    livestock_farming_id = fields.Many2one(
        "spp.create.event.livestock.farming.wizard",
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


class SPPCreateEventLivestockFarmingTechWizard(models.TransientModel):
    _name = "spp.create.event.livestock.farming.tech.wizard"
    _description = "XII. Livestock Farming (Technologies/Techniques)"

    livestock_farming_id = fields.Many2one(
        "spp.create.event.livestock.farming.wizard",
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
