from dateutil.relativedelta import relativedelta

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

    location_id = fields.Many2one("spp.crvs.location")

    no_of_child_under_12_months = fields.Integer(
        "Number of child under 12 months",
        compute="_compute_no_of_child_under_months",
        store=True,
    )

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
    def _compute_no_of_child_under_months(self):
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
                    child_under_12_count = 0
                    group = membership_id.group
                    for member in group.group_membership_ids:
                        if member.individual == rec:
                            continue

                        if not member.individual.birthdate:
                            continue

                        age = member.individual.compute_age_by_month()
                        if age is None:
                            continue

                        if age < 12:
                            child_under_12_count += 1

                    if child_under_12_count:
                        rec.no_of_child_under_12_months = child_under_12_count

    def compute_age_by_month(self):
        self.ensure_one()

        today = fields.Datetime.now().date()
        if self.birthdate:
            delta = relativedelta(today, self.birthdate)
            return delta.months + (delta.years * 12)
        return None
