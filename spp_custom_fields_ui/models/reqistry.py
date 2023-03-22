# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from dateutil.relativedelta import relativedelta

from odoo import fields, models


class Registry(models.Model):
    _inherit = "res.partner"

    def _now(self):
        return fields.Date.today()

    def _relativedelta(self, **kwargs):
        return relativedelta(**kwargs)
