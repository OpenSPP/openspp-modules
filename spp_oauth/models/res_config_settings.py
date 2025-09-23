from odoo import fields, models


class RegistryConfig(models.TransientModel):
    _inherit = "res.config.settings"

    oauth_priv_key = fields.Char(
        string="OAuth Private Key",
        config_parameter="spp_oauth.oauth_priv_key",
    )
    oauth_pub_key = fields.Char(
        string="OAuth Public Key",
        config_parameter="spp_oauth.oauth_pub_key",
    )
