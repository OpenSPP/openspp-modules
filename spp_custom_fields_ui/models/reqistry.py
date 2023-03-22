# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from dateutil.relativedelta import relativedelta

from odoo import fields, models


class Registry(models.Model):
    _inherit = "res.partner"

    def _now(self):
        """Get the current date
        To be used in the custom field compute field code.
        :return: Date - current date
        """
        return fields.Date.today()

    def _relativedelta(self, **kwargs):
        """
        To be used in the custom field compute field code.
        :param kwargs:
        :return: dateutil.relativedelta
        """
        return relativedelta(**kwargs)
