from odoo import api, models


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model
    def search(self, domain, offset=0, limit=None, order=None, count=False):
        res = super().search(domain, offset, limit, order, count)
        if not count and self._name == "payment.acquirer":
            res = res.filtered(lambda a: not a.module_to_buy)
        return res
