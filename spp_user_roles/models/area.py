# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class AreaCustomSPPRole(models.Model):
    _inherit = "spp.area"

    @api.model
    def _name_search(self, name, domain=None, operator="ilike", limit=None, order=None):
        _logger.debug("SPP.AREA: _name_search user: %s" % self.env.user.name)
        if domain is None:
            domain = []
        if self.env.user.center_area_ids:
            domain += [("id", "child_of", self.env.user.center_area_ids.ids)]

        _logger.debug("SPP.AREA: _name_search domain: %s" % domain)
        return super()._name_search(name, domain, operator, limit, order)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        _logger.debug("SPP.AREA: search_read user: %s" % self.env.user.name)
        if domain is None:
            domain = []
        if self.env.user.center_area_ids:
            domain += [("id", "child_of", self.env.user.center_area_ids.ids)]

        _logger.debug("SPP.AREA: search_read domain: %s" % domain)
        return super().search_read(domain, fields, offset, limit, order)

    @api.model
    def web_search_read(self, domain, specification, offset=0, limit=None, order=None, count_limit=None):
        _logger.debug("SPP.AREA: web_search_read user: %s" % self.env.user.name)
        if domain is None:
            domain = []
        if self.env.user.center_area_ids:
            domain += [("id", "child_of", self.env.user.center_area_ids.ids)]

        _logger.debug("SPP.AREA: web_search_read domain: %s" % domain)
        return super().web_search_read(domain, specification, offset, limit, order, count_limit)
