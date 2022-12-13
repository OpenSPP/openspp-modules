from odoo import fields, models


class G2PCycle(models.Model):
    _inherit = "g2p.cycle"

    # Entitlement Basket Fields
    entitlement_basket_id = fields.Many2one("spp.entitlement.basket", "Entitlement Basket")
    # Stock Management Fields
    picking_ids = fields.One2many(
        "stock.picking", "cycle_id", string="Basket Stock Transfers"
    )
    procurement_group_id = fields.Many2one("procurement.group", "Procurement Group")
