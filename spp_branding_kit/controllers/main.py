# ABOUTME: Main controller for OpenSPP Branding Kit
# ABOUTME: Handles custom routes and branding-related endpoints

import json

from werkzeug.wrappers import Response

from odoo import http
from odoo.http import request


class OpenSPPBrandingController(http.Controller):
    """Custom routes for OpenSPP branding"""

    @http.route("/openspp/about", type="http", auth="public")
    def openspp_about(self, **kwargs):
        """Custom about page for OpenSPP"""
        config_parameter = request.env["ir.config_parameter"].sudo()
        return json.dumps(
            {
                "title": "About OpenSPP",
                "version": "1.0.0",
                "system_name": config_parameter.get_param("openspp.system_name", "OpenSPP Platform"),
                "documentation_url": config_parameter.get_param(
                    "openspp.documentation_url", "https://docs.openspp.org"
                ),
                "support_url": config_parameter.get_param("openspp.support_url", "https://openspp.org"),
            }
        )

    @http.route("/web/webclient/version_info", type="json", auth="none")
    def version_info(self):
        """Override version info to show OpenSPP branding"""
        config_parameter = request.env["ir.config_parameter"].sudo()
        system_name = config_parameter.get_param("openspp.system_name", "OpenSPP Platform")
        return {
            "server_version": system_name,
            # Keep the server series aligned with the actual Odoo major version
            "server_serie": "17.0",
            "protocol_version": 1,
        }

    @http.route("/publisher-warranty", type="http", auth="none", csrf=False)
    def publisher_warranty(self, **kwargs):
        """Handle telemetry based on configuration"""
        config_parameter = request.env["ir.config_parameter"].sudo()
        telemetry_enabled = config_parameter.get_param("openspp.telemetry_enabled", "True") == "True"

        if not telemetry_enabled:
            payload = {"status": "disabled", "message": "Telemetry disabled"}
        else:
            # Redirect to OpenSPP telemetry endpoint
            telemetry_endpoint = config_parameter.get_param(
                "openspp.telemetry_endpoint", "https://telemetry.openspp.org"
            )
            payload = {
                "status": "redirected",
                "endpoint": telemetry_endpoint,
                "message": "Telemetry redirected to OpenSPP",
            }

        return Response(json.dumps(payload), content_type="application/json")
