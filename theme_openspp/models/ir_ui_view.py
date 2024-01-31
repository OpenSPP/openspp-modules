import logging

from odoo import models

_logger = logging.getLogger(__name__)


class View(models.Model):
    _inherit = "ir.ui.view"

    def _render_template(self, template, values=None):
        # if template in ['web.login', 'web.webclient_bootstrap']:
        if not values:
            values = {}
        values["title"] = values["app_title"] = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("app_system_name", "OpenSPP")
        )
        return super()._render_template(template, values=values)
