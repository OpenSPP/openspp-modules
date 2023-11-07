from odoo import fields, models


class OpenSPPIndividual(models.Model):
    _inherit = "res.partner"

    ind_is_imported_from_crvs = fields.Boolean("Imported from CRVS")
    # ind_is_updated_from_crvs = fields.Boolean("Updated from CRVS")
