from odoo import models


class SppServicePoint(models.Model):
    _name = "spp.service.point"
    _inherit = ["spp.service.point", "spp.unique.id"]

    def _get_spp_id_prefix(self):
        return "SVP"

    def _get_match_spp_id_pattern(self):
        return r"^SVP_[0-9A-Z]{8}$"
