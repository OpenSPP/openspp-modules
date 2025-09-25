import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class SPPFertilizer(models.Model):
    _name = "spp.fertilizer"
    _description = "Fertilizer Interventions Types"

    name = fields.Char("Fertilizer Interventions Type")
