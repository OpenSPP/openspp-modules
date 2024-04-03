from odoo import api, fields, models


class OpenSPPEventDataIncomeFromNonAgriculture(models.Model):
    _name = "spp.event.inc.non.agri"
    _description = "Non-Agriculture Annual Income Sources (in LAK)"

    salary = fields.Float("Income from Salary")
    wages = fields.Float("Income from Wages")
    handicraft = fields.Float("Income from Handicraft")
    ntfp = fields.Float("Income from NTFPs")
    remittance = fields.Float("Income from Remittance")
    business = fields.Float("Income from Business")
    land_lease = fields.Float("Income from Land Lease")
    other = fields.Float("Other Income from Non-Agriculture")
    total = fields.Float("Total Income from Non-Agriculture", compute="_compute_total")

    @api.depends("salary", "wages", "handicraft", "ntfp", "remittance", "business", "land_lease", "other")
    def _compute_total(self):
        for rec in self:
            rec.total = (
                rec.salary
                + rec.wages
                + rec.handicraft
                + rec.ntfp
                + rec.remittance
                + rec.business
                + rec.land_lease
                + rec.other
            )
