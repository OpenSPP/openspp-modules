# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class SPPInKindEntitlement(models.Model):
    _inherit = "g2p.entitlement.inkind"

    inkind_item_id = fields.Many2one("g2p.program.entitlement.manager.inkind.item", "In-Kind Entitlement Condition")
