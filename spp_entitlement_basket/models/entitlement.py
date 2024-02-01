# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class SPPBasketEntitlement(models.Model):
    _inherit = "g2p.entitlement.inkind"

    # TODO: @edwin: Add to "g2p.entitlement" an entitlement kind selection field.

    entitlement_basket_id = fields.Many2one("spp.entitlement.basket", "Entitlement Basket")
