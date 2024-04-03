from odoo import fields, models


class OpenSPPEventDataAgriculturalTechWS(models.Model):
    _name = "spp.event.agri.tech.ws"
    _description = "IX. Agricultural Technologies During the WS"

    agri_prod_sales_cost_tech_ids = fields.One2many(
        "spp.event.agri.tech.ws.lines",
        "agri_prod_sales_cost_tech_id",
        string="Agricultural Technologies During WS",
    )

    def get_view_id(self):
        """
        This retrieves the View ID of this model
        """
        return self.env["ir.ui.view"].search([("model", "=", self._name), ("type", "=", "form")], limit=1).id


class OpenSPPEventDataAgriculturalTechWSLines(models.Model):
    _name = "spp.event.agri.tech.ws.lines"
    _description = "IX. Agricultural Technologies During the WS"

    agri_prod_sales_cost_tech_id = fields.Many2one(
        "spp.event.agri.tech.ws",
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
