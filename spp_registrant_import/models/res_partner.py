from odoo import models


class Registrant(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "spp.unique.id"]

    def _get_spp_id_prefix(self):
        if not self.is_registrant:
            return ""
        if self.is_group:
            return "GRP"
        return "IND"

    def _get_match_spp_id_pattern(self):
        if not self.is_registrant:
            return ""
        if self.is_group:
            return r"^GRP_[0-9A-Z]{8}$"
        return r"^IND_[0-9A-Z]{8}$"
