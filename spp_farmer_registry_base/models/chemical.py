import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class SPPFarmChemical(models.Model):
    _name = "spp.farm.chemical"
    _description = "Chemical Interventions Types"

    name = fields.Char("Chemical Interventions Type")
