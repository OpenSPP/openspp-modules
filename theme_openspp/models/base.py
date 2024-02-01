from odoo import api, models


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model
    def search(self, domain, offset=0, limit=None, order=None):
        res = super().search(domain, offset, limit, order)
        if self._name == "payment.acquirer":
            res = res.filtered(lambda a: not a.module_to_buy)
        return res
