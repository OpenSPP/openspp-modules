from odoo import api, fields, models


class OpenSPPEventDataAgriculturalTechWS(models.Model):
    _name = "spp.event.agri.tech.ws"
    _description = "IX. Agricultural Technologies During the WS"

    survey_sched = fields.Selection(
        [("1", "Baseline"), ("2", "Midline"), ("3", "Endline")],
        string="Survey Schedule",
    )
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


class OpenSPPEventDataAgriculturalTechWSResPartner(models.Model):
    _inherit = "res.partner"

    active_event_agri_tech_ws = fields.Many2one("spp.event.agri.tech.ws",
                                                compute="_compute_active_event_agri_tech_ws",
                                                store=True)

    ix_survey_schedule = fields.Selection(string="Survey Schedule", related="active_event_agri_tech_ws.survey_sched")
    ix_agri_prod_sales_cost_tech_ids = fields.One2many(
        "spp.event.agri.tech.ws.lines",
        related="active_event_agri_tech_ws.agri_prod_sales_cost_tech_ids",
        string="Agricultural Technologies During WS",
    )

    @api.depends("event_data_ids")
    def _compute_active_event_agri_tech_ws(self):
        """
        This computes the active Agricultural Technologies During the WS event of the group
        """
        for rec in self:
            event_data = rec._get_active_event_id("spp.event.agri.tech.ws")
            rec.active_event_agri_tech_ws = None
            if event_data:
                event_data_res_id = self.env["spp.event.data"].search([("id", "=", event_data)], limit=1).res_id
                rec.active_event_agri_tech_ws = (
                    self.env["spp.event.agri.tech.ws"].search([("id", "=", event_data_res_id)], limit=1).id
                )
