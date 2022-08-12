# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class OpenSPPDashboard(http.Controller):
    @http.route("/tile/details", type="json", auth="user")
    def tile_details(self, **kw):
        """Override the filter if 'active_id' is used"""
        block_obj = request.env["dashboard.block"]
        tile_id = block_obj.sudo().search([("id", "=", kw.get("id"))])
        active_id = kw.get("active_id")
        if tile_id:
            ftr = tile_id.check_filter(tile_id.filter, active_id)
            return {
                "model": tile_id.model_id.model,
                "filter": ftr,
                "model_name": tile_id.model_id.name,
            }
        return False
