from odoo import models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    @property
    def COLOR_ASSET_THEME_URL(self):
        return "/theme_openspp_muk/static/src/scss/colors.scss"

    @property
    def COLOR_ASSET_LIGHT_URL(self):
        return "/theme_openspp_muk/static/src/scss/colors_light.scss"

    @property
    def COLOR_ASSET_DARK_URL(self):
        return "/theme_openspp_muk/static/src/scss/colors_dark.scss"
