import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class Farm(models.Model):
    _inherit = "res.partner"

    farm_prod_ids = fields.One2many("spp.farm.activity", "prod_farm_id", string="Products")
    active_event_cycle2a = fields.Many2one("spp.event.data", compute="_compute_active_event_cycle2a")
    active_event_cycle2b = fields.Many2one("spp.event.data", compute="_compute_active_event_cycle2b")
    active_event_cycle2c = fields.Many2one("spp.event.data", compute="_compute_active_event_cycle2c")
    active_event_cycle3a = fields.Many2one("spp.event.data", compute="_compute_active_event_cycle3a")
    active_event_cycle3b = fields.Many2one("spp.event.data", compute="_compute_active_event_cycle3b")

    @api.depends("event_data_ids")
    def _compute_active_event_cycle2a(self):
        """
        This computes the active farm event of the group
        """
        for rec in self:
            rec.active_event_cycle2a = rec._get_active_event_id("spp.event.cycle2a")

    @api.depends("event_data_ids")
    def _compute_active_event_cycle2b(self):
        """
        This computes the active farm event of the group
        """
        for rec in self:
            rec.active_event_cycle2b = rec._get_active_event_id("spp.event.cycle2b")

    @api.depends("event_data_ids")
    def _compute_active_event_cycle2c(self):
        """
        This computes the active farm event of the group
        """
        for rec in self:
            rec.active_event_cycle2c = rec._get_active_event_id("spp.event.cycle2c")

    @api.depends("event_data_ids")
    def _compute_active_event_cycle3a(self):
        """
        This computes the active farm event of the group
        """
        for rec in self:
            rec.active_event_cycle3a = rec._get_active_event_id("spp.event.cycle3a")

    @api.depends("event_data_ids")
    def _compute_active_event_cycle3b(self):
        """
        This computes the active farm event of the group
        """
        for rec in self:
            rec.active_event_cycle3b = rec._get_active_event_id("spp.event.cycle3b")

    # overwrite for now since we will not create an individual per group in this module
    def create_update_farmer(self, farm):
        pass
