# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import Command, fields, models


class SPPCreateEventAgriculturalWSWizard(models.TransientModel):
    _name = "spp.create.event.agri.ws.wizard"
    _description = "VIII. Agricultural Production, Sales, Costs and Technologies During the WS"

    event_id = fields.Many2one("spp.event.data")

    agri_ws_produce_ids = fields.One2many(
        "spp.create.event.agri.ws.produce.wizard", "agri_ws_id", string="Crops produce"
    )
    agri_ws_cost_ids = fields.One2many(
        "spp.create.event.agri.ws.cost.wizard", "agri_ws_id", string="Production cost per crop"
    )
    experience_dryspell_flood = fields.Integer(
        "Experience any dry spell / " "flood / hailstorm / storm during the WS 2022 cropping season"
    )
    experience_dryspell_flood_dates = fields.Char("If yes, when?")
    experience_pest_disease_outbreak = fields.Integer(
        "Experience any pest or disease outbreak " "on your farmland during the WS 2022 cropping season"
    )
    experience_pest_disease_outbreak_dates = fields.Char("If yes, when?")
    experience_pest_disease_outbreak_type = fields.Char("Type of pest or disease")
    experience_pest_disease_outbreak_affected = fields.Char("Affected crops (crop's code)")

    def create_event(self):
        for rec in self:
            vals_list = {
                "experience_dryspell_flood": rec.experience_dryspell_flood,
                "experience_dryspell_flood_dates": rec.experience_dryspell_flood_dates,
                "experience_pest_disease_outbreak": rec.experience_pest_disease_outbreak,
                "experience_pest_disease_outbreak_dates": rec.experience_pest_disease_outbreak_dates,
                "experience_pest_disease_outbreak_type": rec.experience_pest_disease_outbreak_type,
                "experience_pest_disease_outbreak_affected": rec.experience_pest_disease_outbreak_affected,
            }
            if rec.agri_ws_produce_ids:
                produce_vals = []
                for produce in rec.agri_ws_produce_ids:
                    produce_vals.append(
                        Command.create(
                            {
                                "crop_id": produce.crop_id.id,
                                "cropping_period_sowing": produce.cropping_period_sowing,
                                "cropping_period_harvest": produce.cropping_period_harvest,
                                "harvest_area": produce.harvest_area,
                                "harvest_amount": produce.harvest_amount,
                                "harvest_share": produce.harvest_share,
                                "sales_qty": produce.sales_qty,
                                "sales_price": produce.sales_price,
                                "sales_value": produce.sales_value,
                                "contract_farming": produce.contract_farming,
                                "name_of_partner": produce.name_of_partner,
                            }
                        )
                    )
                vals_list.update({"agri_ws_produce_ids": produce_vals})

                cost_vals = []
                for cost in rec.agri_ws_cost_ids:
                    cost_vals.append(
                        Command.create(
                            {
                                "crop_id": cost.crop_id.id,
                                "labor_input": cost.labor_input,
                                "preparation_farmland": cost.preparation_farmland,
                                "seeds": cost.seeds,
                                "labor_cost": cost.labor_cost,
                                "fertilizer": cost.fertilizer,
                                "pesticide": cost.pesticide,
                                "herbicide": cost.herbicide,
                                "water_fee": cost.water_fee,
                                "tool_equipment": cost.tool_equipment,
                                "other_fees": cost.other_fees,
                                "total_production": cost.total_production,
                            }
                        )
                    )
                vals_list.update({"agri_ws_cost_ids": cost_vals})

            event = self.env["spp.event.agri.ws"].create(vals_list)
            rec.event_id.res_id = event.id

            return event


class SPPCreateEventAgriculturalWSProduceWizard(models.TransientModel):
    _name = "spp.create.event.agri.ws.produce.wizard"
    _description = "Agricultural Production"

    agri_ws_id = fields.Many2one("spp.create.event.agri.ws.wizard")
    crop_id = fields.Many2one("spp.farm.species", string="Crop", domain="[('species_type', '=', 'crop')]")
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


class SPPCreateEventAgriculturalWSCostWizard(models.TransientModel):
    _name = "spp.create.event.agri.ws.cost.wizard"
    _description = "Product cost per crop"

    agri_ws_id = fields.Many2one("spp.create.event.agri.ws.wizard")
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
