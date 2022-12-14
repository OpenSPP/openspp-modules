# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ServicePoint(models.Model):
    _inherit = "spp.service.point"

    product_ids = fields.Many2many(
        "product.product", string="Products", domain=[("type", "=", "product")]
    )
