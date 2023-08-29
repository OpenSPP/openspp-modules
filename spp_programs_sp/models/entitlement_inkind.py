# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class CustomSPPProgramEntitlementInKind(models.Model):
    """
    Add the handling of service points in entitlements
    """

    _inherit = "g2p.entitlement.inkind"

    service_point_ids = fields.Many2many("spp.service.point", string="Service Points")
