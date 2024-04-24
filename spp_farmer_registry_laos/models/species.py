import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class Species(models.Model):
    _inherit = "spp.farm.species"

    name = fields.Char(string="Species Name", translate=True)
