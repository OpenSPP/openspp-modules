# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class EntitlementBasket(models.Model):
    """
    EntitlementBasket is the model for food basket configuration.
    Food baskets are selected in the food basket entitlement manager.

    The field product_ids contains the list of products in a basket with QTY
    and unit of measure that will be distributed to the beneficiaries.

    Setting the active field to false will make a food basket unselectable
    in the food basket entitlement manager.

    """

    _name = "spp.entitlement.basket"
    _description = "Entitlement Basket"
    _order = "id desc"

    name = fields.Char("Entitlement Basket Name", required=True)
    product_ids = fields.One2many("spp.entitlement.basket.product", "basket_id", string="Products")
    product_names = fields.Text(compute="_compute_product_names", readonly=True, store=True)
    active = fields.Boolean(default=True)

    @api.depends("product_ids")
    def _compute_product_names(self):
        """

        :return:
        """
        for rec in self:
            product_names = ""
            for ctr, pr in enumerate(rec.product_ids, start=1):
                product_names += f"{ctr}.) {pr.product_id.name} - {pr.qty} {pr.uom_id.name}\n"
            rec.product_names = product_names


class EntitlementBasketProducts(models.Model):
    """
    EntitlementBasketProducts is the model for the products in food baskets.
    One or more products can be defined per food basket.

    The field product_id is linked to the model product.product.

    """

    _name = "spp.entitlement.basket.product"
    _description = "Entitlement Basket Product"

    basket_id = fields.Many2one("spp.entitlement.basket", "Entitlement Basket", required=True)
    product_id = fields.Many2one("product.product", "Product", domain=[("type", "=", "product")], required=True)
    qty = fields.Integer("QTY", default=1)
    uom_id = fields.Many2one("uom.uom", "Unit of Measure", related="product_id.uom_id")
