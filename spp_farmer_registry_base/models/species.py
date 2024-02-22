import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class Species(models.Model):
    _name = "spp.farm.species"
    _description = "Species"

    name = fields.Char(string="Species Name")
    description = fields.Text()
    image = fields.Binary()
    species_type = fields.Selection(
        [("aquaculture", "Aquaculture"), ("crop", "Crop"), ("livestock", "Livestock")],
        string="Type",
        default="crop",
    )
