# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class ResPartnerCustomSPP(models.Model):
    _inherit = "res.partner"

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        """
        Override search_read to inject the center_area_ids in domain
        :param domain: String domain
        :param fields: List of fields
        :param offset: Query offset
        :param limit: Query limit
        :param order: Query order
        :return:
        """
        _logger.debug("FILTER: user: %s" % self.env.user.name)
        # Determine if the domain is for group or individual
        # grp_dom = list(filter(lambda x: x[0] == "is_group" and x[2], domain))
        # _logger.info("FILTER: grp_dom: %s" % grp_dom)
        if self.env.user.center_area_ids:
            # if grp_dom:
            domain.append(("area_id", "child_of", self.env.user.center_area_ids.ids))

        res = super().search_read(domain, fields, offset, limit, order)
        _logger.debug("FILTER: domain: %s" % domain)
        return res
