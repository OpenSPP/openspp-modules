# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SPPCreateEventIncomeFromNonAgribusinessWizard(models.TransientModel):
    _name = "spp.create.event.inc.non.agri.wizard"
    _description = "XIV. Non-Agriculture Annual Income Sources (in LAK)"

    event_id = fields.Many2one("spp.event.data")

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

    def create_event(self):
        for rec in self:
            vals_list = {
                "salary": rec.salary,
                "wages": rec.wages,
                "handicraft": rec.handicraft,
                "ntfp": rec.ntfp,
                "remittance": rec.remittance,
                "business": rec.business,
                "land_lease": rec.land_lease,
                "other": rec.other,
            }

            event = self.env["spp.event.inc.non.agri"].create(vals_list)
            rec.event_id.res_id = event.id

            return event
