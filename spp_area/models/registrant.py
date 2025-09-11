# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class G2PRegistrant(models.Model):
    _inherit = "res.partner"

    @api.model
    def _get_area_domain(self):
        """
        This set up the domain of the area base on its kind
        """
        area_id = self.env.ref("spp_area_base.admin_area_kind").id
        return [("kind", "=", area_id)]

    @api.model
    def _prepare_domain(self, domain):
        domain = domain or []
        domain += [("area_id", "child_of", self.env.user.center_area_ids.ids)] if self.env.user.center_area_ids else []
        return domain

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        domain = self._prepare_domain(domain)
        return super().search_read(domain, fields, offset, limit, order)

    @api.model
    def web_search_read(self, domain, specification, offset=0, limit=None, order=None, count_limit=None):
        domain = self._prepare_domain(domain)
        return super().web_search_read(domain, specification, offset, limit, order, count_limit)

    # Custom Fields
    area_id = fields.Many2one(
        "spp.area",
        "Area",
        domain=_get_area_domain,
    )
