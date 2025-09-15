import logging

from odoo import models

from ..utils import get_branding_config

_logger = logging.getLogger(__name__)


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        """Override session info to customize branding"""
        result = super().session_info()

        # Add OpenSPP configuration
        result.update(get_branding_config(self.env))

        # Customize server version info while keeping the correct Odoo series
        if "server_version_info" in result:
            result["server_version_info"] = ["OpenSPP", "17.0", "", "", ""]

        return result
