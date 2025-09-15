# ABOUTME: Override ir.http to customize HTTP behavior and configure telemetry
# ABOUTME: Provides session info for frontend debranding and telemetry settings

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        """Override session info to customize branding"""
        result = super().session_info()

        IrConfig = self.env["ir.config_parameter"].sudo()

        # Add OpenSPP configuration
        result.update(
            {
                "openspp_system_name": IrConfig.get_param("openspp.system_name", "OpenSPP Platform"),
                "openspp_documentation_url": IrConfig.get_param(
                    "openspp.documentation_url", "https://docs.openspp.org"
                ),
                "openspp_support_url": IrConfig.get_param("openspp.support_url", "https://openspp.org"),
                "openspp_show_powered_by": IrConfig.get_param("openspp.show_powered_by", "True") == "True",
                "openspp_telemetry_enabled": IrConfig.get_param("openspp.telemetry_enabled", "True") == "True",
                "openspp_telemetry_endpoint": IrConfig.get_param(
                    "openspp.telemetry_endpoint", "https://telemetry.openspp.org"
                ),
            }
        )

        # Customize server version info while keeping the correct Odoo series
        if "server_version_info" in result:
            result["server_version_info"] = ["OpenSPP", "17.0", "", "", ""]

        return result
