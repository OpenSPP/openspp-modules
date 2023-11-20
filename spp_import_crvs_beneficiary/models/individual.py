from odoo import api, fields, models


class OpenSPPIndividual(models.Model):
    _inherit = "res.partner"

    ind_is_imported_from_crvs = fields.Boolean(
        "Imported from CRVS", compute="_compute_ind_is_imported_from_crvs"
    )

    crvs_import_ids = fields.One2many(
        "spp.crvs.imported.individuals", "individual_id", "CRVS Import"
    )

    is_mother = fields.Boolean("A Mother", compute="_compute_is_mother", store=True)
    youngest_child_age = fields.Integer(
        "Youngest Child Age (Year)", compute="_compute_youngest_child_age", store=True
    )

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
                        self.env.ref(
                            "g2p_registry_membership.group_membership_kind_head"
                        ).id,
                    ),
                    ("is_created_from_crvs", "=", True),
                ]
            )
            if membership_ids:
                rec.is_mother = True
            else:
                rec.is_mother = False

    @api.depends("individual_membership_ids")
    def _compute_youngest_child_age(self):
        for rec in self:
            if rec.is_mother:
                membership_id = self.env["g2p.group.membership"].search(
                    [
                        ("id", "in", rec.individual_membership_ids.ids),
                        ("is_created_from_crvs", "=", True),
                    ],
                    limit=1,
                )

                if membership_id:
                    youngest_child_age = None
                    group = membership_id.group
                    for member in group.group_membership_ids:
                        if member.individual == rec:
                            continue

                        age = member.individual.age
                        if age.isdigit():
                            age = int(age)
                        else:
                            continue

                        if youngest_child_age is None:
                            youngest_child_age = age
                        elif age < youngest_child_age:
                            youngest_child_age = age

                    rec.youngest_child_age = youngest_child_age
