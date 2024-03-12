import json
import logging

import pyproj
from shapely.geometry import mapping
from shapely.ops import transform

from odoo import Command, api, fields, models

_logger = logging.getLogger(__name__)


class Farm(models.Model):
    _inherit = "res.partner"

    farm_prod_ids = fields.One2many("spp.farm.activity", "prod_farm_id", string="Products")
    active_farm_event = fields.Many2one("spp.event.data", compute="_compute_active_farm_event")

    @api.depends("event_data_ids")
    def _compute_active_farm_event(self):
        """
        This computes the active farm event of the group
        """
        for rec in self:
            rec.active_house_visit = rec._get_active_event_id("spp.event.farm")
