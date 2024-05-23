# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class ProductTemplateCustom(models.Model):
    _inherit = "product.template"

    is_locked = fields.Boolean(string="Locked", default=False)

    def get_is_locked(self):
        self.ensure_one()
        return {"is_locked": self.is_locked}

    @api.model
    def get_entitlement_product(self):
        return self.env.ref("spp_pos.entitlement_product").id
