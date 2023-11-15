from odoo import fields, models


class OpenSPPRegistry(models.Model):
    # Applicable to both Individual and Group Registry

    _inherit = "res.partner"

    data_source_id = fields.Many2one(
        "spp.data.source",
        readonly=True,
    )
