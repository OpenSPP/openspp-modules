from odoo import models


class SppArea(models.Model):
    _name = "spp.area"
    _inherit = ["spp.area", "spp.unique.id"]

    def _get_spp_id_prefix(self):
        return "LOC"

    def _get_match_spp_id_pattern(self):
        return r"^LOC_[0-9A-Z]{8}$"
