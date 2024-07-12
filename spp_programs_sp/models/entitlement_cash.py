# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class CustomSPPProgramEntitlementCash(models.Model):
    """
    Add the handling of service points in entitlements
    """

    _inherit = "g2p.entitlement"

    service_point_ids = fields.Many2many(
        comodel_name="spp.service.point",
        relation="g2p_entitlement_spp_service_point_rel",
        column1="g2p_entitlement_id",
        column2="spp_service_point_id",
        string="Service Points",
    )
    service_point_id = fields.Many2one("spp.service.point", "Service Point")
