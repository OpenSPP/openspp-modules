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
                product_names += f"{ctr}.) {pr.product_id.name}"
                if pr.alt_product_ids:
                    product_names += " - Alternate Products: " + ", ".join(
                        pr.alt_product_ids.mapped("name")
                    )
                product_names += ". \n"
            rec.product_names = product_names


class EntitlementBasketProducts(models.Model):
    _name = "spp.entitlement.basket.product"
    _description = "Entitlement Basket Product"

    basket_id = fields.Many2one("spp.entitlement.basket", "Entitlement Basket", required=True)
    product_id = fields.Many2one(
        "product.product", "Product", domain=[("type", "=", "product")], required=True
    )
    alt_product_ids = fields.Many2many(
        "product.product",
        string="Alternate Products",
        domain=[("type", "=", "product")],
    )
    qty = fields.Integer("QTY")
