# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class ResPartnerCustomSPP(models.Model):
    _inherit = "res.partner"

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        _logger.debug("RES.PARTNER: search_read user: %s" % self.env.user.name)
        if domain is None:
            domain = []
        if self.env.user.center_area_ids:
            domain += [("area_id", "child_of", self.env.user.center_area_ids.ids)]

        res = super().search_read(domain, fields, offset, limit, order)
        _logger.debug("RES.PARTNER: search_read domain: %s" % domain)
        return res

    @api.model
    def web_search_read(self, domain, specification, offset=0, limit=None, order=None, count_limit=None):
        _logger.debug("RES.PARTNER: web_search_read user: %s" % self.env.user.name)
        if domain is None:
            domain = []
        if self.env.user.center_area_ids:
            domain += [("area_id", "child_of", self.env.user.center_area_ids.ids)]

        _logger.debug("RES.PARTNER: web_search_read domain: %s" % domain)
        return super().web_search_read(domain, specification, offset, limit, order, count_limit)
