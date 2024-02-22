import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class SPPChemical(models.Model):
    # TODO: rename to spp.farm.chemical
    _name = "spp.chemical"
    _description = "Chemical Interventions Types"

    name = fields.Char("Chemical Interventions Type")
