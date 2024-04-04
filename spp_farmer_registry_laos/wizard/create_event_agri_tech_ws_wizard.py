# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import Command, fields, models


class SPPCreateEventAgriculturalTechWSWizard(models.TransientModel):
    _name = "spp.create.event.agri.tech.ws.wizard"
    _description = "IX. Agricultural Technologies During the WS"

    event_id = fields.Many2one("spp.event.data")
    survey_sched = fields.Selection(
        [("1", "Baseline"), ("2", "Midline"), ("3", "Endline")],
        string="Survey Schedule",
    )
    agri_prod_sales_cost_tech_ids = fields.One2many(
        "spp.create.event.agri.tech.ws.lines.wizard",
        "agri_prod_sales_cost_tech_id",
        string="Agricultural Technologies During WS",
    )

    def create_event(self):
        for rec in self:
            vals_list = {
                "survey_sched": rec.survey_sched
            }
            if rec.agri_prod_sales_cost_tech_ids:
                tech_vals = []
                for tech in rec.agri_prod_sales_cost_tech_ids:
                    tech_vals.append(
                        Command.create(
                            {
                                "crop_id": tech.crop_id.id,
                                "org_felt_pest_herb": tech.org_felt_pest_herb,
                                "greenhouse": tech.greenhouse,
                                "multing": tech.multing,
                                "irrigation_normal": tech.irrigation_normal,
                                "water_pump": tech.water_pump,
                                "drip_irrigation": tech.drip_irrigation,
                                "sprinkler": tech.sprinkler,
                                "machine_harvest": tech.machine_harvest,
                                "dry_processing": tech.dry_processing,
                                "post_harvest_treatment": tech.post_harvest_treatment,
                                "other": tech.other,
                            }
                        )
                    )
                vals_list.update({"agri_prod_sales_cost_tech_ids": tech_vals})

                event = self.env["spp.event.agri.tech.ws"].create(vals_list)
                rec.event_id.res_id = event.id

                return event


class SPPCreateEventAgriculturalTechWSLinesWizard(models.TransientModel):
    _name = "spp.create.event.agri.tech.ws.lines.wizard"
    _description = "IX. Agricultural Technologies During the WS"

    agri_prod_sales_cost_tech_id = fields.Many2one(
        "spp.create.event.agri.tech.ws.wizard",
        string="Agricultural Technologies During WS",
    )
    crop_id = fields.Many2one("spp.farm.species", string="Crop", domain="[('species_type', '=', 'crop')]")
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
