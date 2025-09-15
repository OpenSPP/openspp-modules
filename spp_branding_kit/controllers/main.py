import json

from werkzeug.wrappers import Response

from odoo import http
from odoo.http import request

from odoo.addons.portal.controllers.web import Home


class OpenSPPHome(Home):
    """Restrict debug mode to administrators when enabled via parameter."""

    @http.route()
    def web_client(self, s_action=None, **kw):
        # Enforce optional debug restriction before rendering
        try:
            config_parameter = request.env["ir.config_parameter"].sudo()
            debug_admin_only = config_parameter.get_param("openspp.debug.admin_only", "True") == "True"
        except Exception:  # pragma: no cover - defensive
            debug_admin_only = True

        # Detect debug flag from kwargs or query string
        has_debug = bool(kw.get("debug")) or ("debug" in (request.httprequest.args or {}))
        if debug_admin_only and has_debug:
            uid = request.session.uid
            # If not logged in or not admin, strip debug and redirect
            if not uid or not request.env.user._is_admin():
                kw.pop("debug", None)
                args = {k: v for k, v in request.httprequest.args.items() if k != "debug"}
                return request.redirect("/web", query=args)

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
                "system_name": config_parameter.get_param("openspp.system.name", "OpenSPP Platform"),
                "documentation_url": config_parameter.get_param(
                    "openspp.documentation.url", "https://docs.openspp.org"
                ),
                "support_url": config_parameter.get_param("openspp.support.url", "https://openspp.org"),
            }
        )

    @http.route("/web/webclient/version_info", type="json", auth="none")
    def version_info(self):
        """Override version info to show OpenSPP branding"""
        config_parameter = request.env["ir.config_parameter"].sudo()
        system_name = config_parameter.get_param("openspp.system.name", "OpenSPP Platform")
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
        telemetry_enabled = config_parameter.get_param("openspp.telemetry.enabled", "True") == "True"

        if not telemetry_enabled:
            payload = {"status": "disabled", "message": "Telemetry disabled"}
        else:
            # Redirect to OpenSPP telemetry endpoint
            telemetry_endpoint = config_parameter.get_param(
                "openspp.telemetry.endpoint", "https://telemetry.openspp.org"
            )
            payload = {
                "status": "redirected",
                "endpoint": telemetry_endpoint,
                "message": "Telemetry redirected to OpenSPP",
            }

        return Response(json.dumps(payload), content_type="application/json")
