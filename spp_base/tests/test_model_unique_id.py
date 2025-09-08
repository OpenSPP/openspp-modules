# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SppUniqueIdTest(models.Model):
    _name = "spp.unique.id.test"
    _inherit = "spp.unique.id"
    _description = "Test Model for spp.unique.id"
    _log_access = False  # Avoid creating unnecessary log entries

    name = fields.Char("Name")
    create_date = fields.Datetime("Creation Date", default=fields.Datetime.now)

    def _get_spp_id_prefix(self):
        return "TEST"

    def _get_match_spp_id_pattern(self):
        return r"^TEST_[2-9A-HJ-NP-Z]{8}$"
