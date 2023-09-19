from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    maximum_daily_recompute_count = fields.Integer(
        string="Maximum Daily Recompute Records Count",
        default=10_000,
        config_parameter="spp.maximum_daily_recompute_count",
        help="Maximum number of records for synchronous recomputing fields.",
    )
