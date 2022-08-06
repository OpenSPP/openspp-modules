# Part of Newlogic G2P. See LICENSE file for full copyright and licensing details.
import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class G2PIndividual(models.Model):
    _inherit = "res.partner"

    family_name = fields.Char("Family Name", translate=True)
    given_name = fields.Char("Given Name", translate=True)
    addl_name = fields.Char("Additional Name", translate=True)
    birth_place = fields.Char("Birth Place")
    birthdate_not_exact = fields.Boolean("Birthdate not exact")
    birthdate = fields.Date("Date of Birth")
    age = fields.Char(compute="_compute_calc_age", string="Age", size=50, readonly=True)
    gender = fields.Selection(
        [("Female", "Female"), ("Male", "Male"), ("Other", "Other")],
        "Gender",
    )

    @api.onchange("is_group", "family_name", "given_name", "addl_name")
    def name_change(self):
        vals = {}
        if not self.is_group:
            name = ""
            if self.family_name:
                name += self.family_name + ", "
            if self.given_name:
                name += self.given_name + " "
            if self.addl_name:
                name += self.addl_name + " "
            vals.update({"name": name.upper()})
            self.update(vals)

    @api.depends("birthdate")
    def _compute_calc_age(self):
        for line in self:
            line.age = self.compute_age_from_dates(line.birthdate)

    def compute_age_from_dates(self, partner_dob):
        now = datetime.strptime(str(fields.Datetime.now())[:10], "%Y-%m-%d")
        if partner_dob:
            dob = partner_dob
            delta = relativedelta(now, dob)
            # years_months_days = str(delta.years) +"y "+ str(delta.months) +"m "+ str(delta.days)+"d"
            years_months_days = str(delta.years)
        else:
            years_months_days = "No Birthdate!"
        return years_months_days
