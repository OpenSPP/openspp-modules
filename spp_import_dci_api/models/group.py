from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class OpenSPPGroup(models.Model):
    _inherit = "res.partner"

    grp_is_created_from_crvs = fields.Boolean("Group Imported from CRVS", store=True)

    no_of_child_under_12_months = fields.Integer(
        "Number of child under 12 months",
        compute="_compute_child_under_no_of_months",
        store=True,
    )

    child_under_12_birthplace = fields.Text(
        "Child under 12 months birthplace",
        compute="_compute_child_under_no_of_months",
        store=True,
    )

    @api.depends("group_membership_ids")
    def _compute_child_under_no_of_months(self):
        head = self.env.ref("g2p_registry_membership.group_membership_kind_head").id
        for rec in self:
            if rec.is_registrant and rec.is_group and rec.group_membership_ids:
                child_under_12_count = 0
                child_under_12_birthplace = []
                for member in rec.group_membership_ids:
                    if head in member.kind.ids:
                        continue
                    if not member.individual_birthdate:
                        continue

                    age = member.individual.compute_age_by_month()

                    if age is None:
                        continue

                    if age < 12:
                        child_under_12_count += 1
                        if member.individual.birth_place:
                            child_under_12_birthplace.append(member.individual.birth_place)

                if child_under_12_count:
                    rec.no_of_child_under_12_months = child_under_12_count
                if child_under_12_birthplace:
                    rec.child_under_12_birthplace = ",".join(child_under_12_birthplace)

    def compute_age_by_month(self):
        self.ensure_one()

        today = fields.Datetime.now().date()
        if self.birthdate:
            delta = relativedelta(today, self.birthdate)
            return delta.months + (delta.years * 12)
        return None
