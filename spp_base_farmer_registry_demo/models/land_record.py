from odoo import fields, models


class LandRecord(models.Model):
    _inherit = "spp.land.record"

    ke_access_cities_reg = fields.Float(
        string="Estimated cumulative travel time/cost to the nearest regional city",
        readonly=True,
    )
