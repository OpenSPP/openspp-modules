# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class OpenSPPEntitlement(models.Model):
    _inherit = "g2p.entitlement"

    @api.model
    def get_entitlement_code(self, code):
        _logger.info("Code: %s", code["code"])
        data = self.env["g2p.entitlement"].search([("code", "=", code["code"])])
        if data:
            entitlement = {
                "code": data[0].code,
                "amount": data[0].initial_amount,
                "status": "Success",
            }
            return entitlement
        else:
            entitlement = {"code": 0, "amount": 0, "status": "QR Doesn't Exist"}
            return entitlement
