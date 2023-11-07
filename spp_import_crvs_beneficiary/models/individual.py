from odoo import api, fields, models


class OpenSPPIndividual(models.Model):
    _inherit = "res.partner"

    ind_is_imported_from_crvs = fields.Boolean(
        "Imported from CRVS", compute="_compute_ind_is_imported_from_crvs", store=True
    )

    crvs_import_ids = fields.One2many(
        "spp.crvs.imported.individuals", "individual_id", "CRVS Import"
    )

    @api.depends("crvs_import_ids")
    def _compute_ind_is_imported_from_crvs(self):
        for rec in self:
            if rec.crvs_import_ids:
                rec.ind_is_imported_from_crvs = True
            else:
                rec.ind_is_imported_from_crvs = False
