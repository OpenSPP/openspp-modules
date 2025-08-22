# ABOUTME: Main controller for OpenSPP Branding Kit
# ABOUTME: Handles custom routes, branding overrides, and security enforcement

import json

from odoo import http
from odoo.http import request

from odoo.addons.portal.controllers.web import Home


class OpenSPPHome(Home):
    """Override Home controller to enforce branding and security settings"""

    @http.route()
    def web_client(self, s_action=None, **kw):
        """Override web client to enforce debug mode restrictions"""
        # Check if debug mode is restricted to admins BEFORE rendering
        if kw.get("debug", False):
            config_parameter = request.env["ir.config_parameter"].sudo()
            debug_admin_only = config_parameter.get_param("openspp.debug_admin_only", "True") == "True"

            if debug_admin_only and request.session.uid:
                # Check if current user is admin
                if not request.env.user._is_admin():
                    # Remove debug parameter and redirect
                    kw.pop("debug", None)
                    return request.redirect("/web", 303)

        return super().web_client(s_action, **kw)


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
            "server_serie": "1.0",
            "protocol_version": 1,
        }

    @http.route("/publisher-warranty", type="http", auth="none", csrf=False)
    def publisher_warranty(self, **kwargs):
        """Handle telemetry based on configuration"""
        config_parameter = request.env["ir.config_parameter"].sudo()
        telemetry_enabled = config_parameter.get_param("openspp.telemetry_enabled", "True") == "True"

        if not telemetry_enabled:
            return json.dumps({"status": "disabled", "message": "Telemetry disabled"})
        else:
            # Redirect to OpenSPP telemetry endpoint
            telemetry_endpoint = config_parameter.get_param(
                "openspp.telemetry_endpoint", "https://telemetry.openspp.org"
            )
            return json.dumps(
                {"status": "redirected", "endpoint": telemetry_endpoint, "message": "Telemetry redirected to OpenSPP"}
            )
