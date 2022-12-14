# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class EntitlementBasket(models.Model):
    _name = "spp.entitlement.basket"
    _description = "Entitlement Basket"
    _order = "id desc"

    name = fields.Char("Entitlement Basket Name", required=True)
    product_ids = fields.One2many(
        "spp.entitlement.basket.product", "basket_id", string="Products"
    )
    product_names = fields.Text(
        compute="_compute_product_names", readonly=True, store=True
    )
    active = fields.Boolean(default=True)

    @api.depends("product_ids")
    def _compute_product_names(self):
        for rec in self:
            product_names = ""
            for ctr, pr in enumerate(rec.product_ids, start=1):
                product_names += (
                    f"{ctr}.) {pr.product_id.name} - {pr.qty} {pr.uom_id.name}\n"
                )
            rec.product_names = product_names


class EntitlementBasketProducts(models.Model):
    _name = "spp.entitlement.basket.product"
    _description = "Entitlement Basket Product"

    basket_id = fields.Many2one(
        "spp.entitlement.basket", "Entitlement Basket", required=True
    )
    product_id = fields.Many2one(
        "product.product", "Product", domain=[("type", "=", "product")], required=True
    )
    qty = fields.Integer("QTY", default=1)
    uom_id = fields.Many2one("uom.uom", "Unit of Measure", related="product_id.uom_id")
