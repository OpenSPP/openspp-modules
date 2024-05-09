from odoo import api, fields, models


class OpenSPPIndividual(models.Model):
    _inherit = "res.partner"

    ind_is_imported_from_crvs = fields.Boolean(
        "Individual Imported from CRVS", compute="_compute_ind_is_imported_from_crvs"
    )

    crvs_import_ids = fields.One2many("spp.crvs.imported.individuals", "individual_id", "CRVS Import")

    is_mother = fields.Boolean("A Mother", compute="_compute_is_mother", store=True)

    location_id = fields.Many2one("spp.crvs.location")

    @api.depends("crvs_import_ids")
    def _compute_ind_is_imported_from_crvs(self):
        for rec in self:
            if rec.crvs_import_ids:
                rec.ind_is_imported_from_crvs = True
            else:
                rec.ind_is_imported_from_crvs = False

    @api.depends("individual_membership_ids")
    def _compute_is_mother(self):
        for rec in self:
            membership_ids = self.env["g2p.group.membership"].search(
                [
                    ("id", "in", rec.individual_membership_ids.ids),
                    (
                        "kind",
                        "=",
                        self.env.ref("g2p_registry_membership.group_membership_kind_head").id,
                    ),
                    ("is_created_from_crvs", "=", True),
                ]
            )
            if membership_ids:
                rec.is_mother = True
            else:
                rec.is_mother = False
