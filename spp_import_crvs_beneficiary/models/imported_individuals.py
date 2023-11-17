import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class SPPCRVSImportedIndividuals(models.Model):
    _name = "spp.crvs.imported.individuals"
    _description = "CRVS Imported Individuals"

    fetch_crvs_id = fields.Many2one(
        "spp.fetch.crvs.beneficiary",
        required=True,
        auto_join=True,
    )

    individual_id = fields.Many2one(
        "res.partner",
        required=True,
        domain=[("is_group", "=", False), ("is_registrant", "=", True)],
        auto_join=True,
    )

    is_created = fields.Boolean("Created?")
    is_updated = fields.Boolean("Updated?")
