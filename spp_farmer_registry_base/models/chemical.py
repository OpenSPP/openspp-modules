import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SPPChemical(models.Model):
    _name = "spp.chemical"
    _description = "Chemical Interventions Types"

    name = fields.Char("Chemical Interventions Type")
