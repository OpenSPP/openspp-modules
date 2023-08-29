# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class CustomG2PProgram(models.Model):
    """
    Add the handling of service points in entitlements
    """

    _inherit = "g2p.program"

    store_sp_in_entitlements = fields.Boolean("Store Service Points to Entitlements")
