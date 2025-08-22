# ABOUTME: Unit tests for the controllers in spp_branding_kit
# ABOUTME: Tests OpenSPPHome and OpenSPPBrandingController

import json
from unittest.mock import MagicMock, patch

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestOpenSPPHome(TransactionCase):
    def setUp(self):
        super().setUp()
        self.IrConfigParam = self.env["ir.config_parameter"].sudo()

    def test_web_client_removes_debug_for_non_admin(self):
        """Test that debug mode is removed for non-admin users"""
        from ..controllers.main import OpenSPPHome

        # Set debug_admin_only to True
        self.IrConfigParam.set_param("openspp.debug_admin_only", "True")

        # Create a non-admin user
        non_admin_user = self.env["res.users"].create(
            {
                "name": "Test Non-Admin",
                "login": "test_non_admin",
                "email": "test@example.com",
            }
        )

        # Mock request
        with patch("spp_branding_kit.controllers.main.request") as mock_request:
            mock_request.env = self.env.sudo(non_admin_user)
            mock_request.session.uid = non_admin_user.id
            mock_request.env.user = non_admin_user
            mock_request.redirect = MagicMock(return_value="redirect_response")

            controller = OpenSPPHome()

            # Mock super().web_client
            with patch.object(OpenSPPHome.__bases__[0], "web_client", return_value="web_client_response"):
                # Test with debug=True for non-admin
                result = controller.web_client(debug=True)

                # Should redirect without debug
                mock_request.redirect.assert_called_once_with("/web", 303)
                self.assertEqual(result, "redirect_response")

    def test_web_client_allows_debug_for_admin(self):
        """Test that debug mode is allowed for admin users"""
        from ..controllers.main import OpenSPPHome

        # Set debug_admin_only to True
        self.IrConfigParam.set_param("openspp.debug_admin_only", "True")

        # Use admin user
        admin_user = self.env.ref("base.user_admin")

        # Mock request
        with patch("spp_branding_kit.controllers.main.request") as mock_request:
            mock_request.env = self.env.sudo(admin_user)
            mock_request.session.uid = admin_user.id
            mock_request.env.user = admin_user

            controller = OpenSPPHome()

            # Mock super().web_client
            with patch.object(OpenSPPHome.__bases__[0], "web_client", return_value="web_client_response") as mock_super:
                # Test with debug=True for admin
                result = controller.web_client(debug=True)

                # Should call super with debug parameter
                mock_super.assert_called_once_with(debug=True)
                self.assertEqual(result, "web_client_response")

    def test_web_client_allows_debug_when_disabled(self):
        """Test that debug mode is allowed for all when debug_admin_only is False"""
        from ..controllers.main import OpenSPPHome

        # Set debug_admin_only to False
        self.IrConfigParam.set_param("openspp.debug_admin_only", "False")

        # Create a non-admin user
        non_admin_user = self.env["res.users"].create(
            {
                "name": "Test User",
                "login": "test_user",
                "email": "test@example.com",
            }
        )

        # Mock request
        with patch("spp_branding_kit.controllers.main.request") as mock_request:
            mock_request.env = self.env.sudo(non_admin_user)
            mock_request.session.uid = non_admin_user.id
            mock_request.env.user = non_admin_user

            controller = OpenSPPHome()

            # Mock super().web_client
            with patch.object(OpenSPPHome.__bases__[0], "web_client", return_value="web_client_response") as mock_super:
                # Test with debug=True for non-admin
                result = controller.web_client(debug=True)

                # Should call super with debug parameter
                mock_super.assert_called_once_with(debug=True)
                self.assertEqual(result, "web_client_response")

    def test_web_client_without_debug(self):
        """Test web_client without debug parameter"""
        from ..controllers.main import OpenSPPHome

        controller = OpenSPPHome()

        # Mock super().web_client
        with patch.object(OpenSPPHome.__bases__[0], "web_client", return_value="web_client_response") as mock_super:
            # Test without debug parameter
            result = controller.web_client()

            # Should call super without modifications
            mock_super.assert_called_once_with()
            self.assertEqual(result, "web_client_response")


@tagged("post_install", "-at_install")
class TestOpenSPPBrandingController(TransactionCase):
    def setUp(self):
        super().setUp()
        self.IrConfigParam = self.env["ir.config_parameter"].sudo()

    def test_openspp_about_route(self):
        """Test the /openspp/about route"""
        from ..controllers.main import OpenSPPBrandingController

        # Set custom configuration
        self.IrConfigParam.set_param("openspp.system_name", "Test System")
        self.IrConfigParam.set_param("openspp.documentation_url", "https://test-docs.org")
        self.IrConfigParam.set_param("openspp.support_url", "https://test-support.org")

        # Mock request
        with patch("spp_branding_kit.controllers.main.request") as mock_request:
            mock_request.env = self.env

            controller = OpenSPPBrandingController()
            result = controller.openspp_about()

            # Parse the JSON response
            data = json.loads(result)

            self.assertEqual(data["title"], "About OpenSPP")
            self.assertEqual(data["version"], "1.0.0")
            self.assertEqual(data["system_name"], "Test System")
            self.assertEqual(data["documentation_url"], "https://test-docs.org")
            self.assertEqual(data["support_url"], "https://test-support.org")

    def test_openspp_about_route_with_defaults(self):
        """Test the /openspp/about route with default values"""
        from ..controllers.main import OpenSPPBrandingController

        # Clear any existing parameters
        self.IrConfigParam.search([("key", "=like", "openspp.%")]).unlink()

        # Mock request
        with patch("spp_branding_kit.controllers.main.request") as mock_request:
            mock_request.env = self.env

            controller = OpenSPPBrandingController()
            result = controller.openspp_about()

            # Parse the JSON response
            data = json.loads(result)

            self.assertEqual(data["title"], "About OpenSPP")
            self.assertEqual(data["version"], "1.0.0")
            self.assertEqual(data["system_name"], "OpenSPP Platform")
            self.assertEqual(data["documentation_url"], "https://docs.openspp.org")
            self.assertEqual(data["support_url"], "https://openspp.org")

    def test_version_info_route(self):
        """Test the /web/webclient/version_info route"""
        from ..controllers.main import OpenSPPBrandingController

        # Set custom system name
        self.IrConfigParam.set_param("openspp.system_name", "Custom OpenSPP")

        # Mock request
        with patch("spp_branding_kit.controllers.main.request") as mock_request:
            mock_request.env = self.env

            controller = OpenSPPBrandingController()
            result = controller.version_info()

            self.assertEqual(result["server_version"], "Custom OpenSPP")
            self.assertEqual(result["server_serie"], "1.0")
            self.assertEqual(result["protocol_version"], 1)

    def test_publisher_warranty_telemetry_enabled(self):
        """Test publisher warranty route when telemetry is enabled"""
        from ..controllers.main import OpenSPPBrandingController

        # Enable telemetry
        self.IrConfigParam.set_param("openspp.telemetry_enabled", "True")
        self.IrConfigParam.set_param("openspp.telemetry_endpoint", "https://custom-telemetry.org")

        # Mock request
        with patch("spp_branding_kit.controllers.main.request") as mock_request:
            mock_request.env = self.env

            controller = OpenSPPBrandingController()
            result = controller.publisher_warranty()

            # Parse the JSON response
            data = json.loads(result)

            self.assertEqual(data["status"], "redirected")
            self.assertEqual(data["endpoint"], "https://custom-telemetry.org")
            self.assertEqual(data["message"], "Telemetry redirected to OpenSPP")

    def test_publisher_warranty_telemetry_disabled(self):
        """Test publisher warranty route when telemetry is disabled"""
        from ..controllers.main import OpenSPPBrandingController

        # Disable telemetry
        self.IrConfigParam.set_param("openspp.telemetry_enabled", "False")

        # Mock request
        with patch("spp_branding_kit.controllers.main.request") as mock_request:
            mock_request.env = self.env

            controller = OpenSPPBrandingController()
            result = controller.publisher_warranty()

            # Parse the JSON response
            data = json.loads(result)

            self.assertEqual(data["status"], "disabled")
            self.assertEqual(data["message"], "Telemetry disabled")

    def test_publisher_warranty_with_default_endpoint(self):
        """Test publisher warranty route with default telemetry endpoint"""
        from ..controllers.main import OpenSPPBrandingController

        # Enable telemetry but don't set custom endpoint
        self.IrConfigParam.set_param("openspp.telemetry_enabled", "True")
        # Clear telemetry endpoint if exists
        param = self.IrConfigParam.search([("key", "=", "openspp.telemetry_endpoint")])
        if param:
            param.unlink()

        # Mock request
        with patch("spp_branding_kit.controllers.main.request") as mock_request:
            mock_request.env = self.env

            controller = OpenSPPBrandingController()
            result = controller.publisher_warranty()

            # Parse the JSON response
            data = json.loads(result)

            self.assertEqual(data["status"], "redirected")
            self.assertEqual(data["endpoint"], "https://telemetry.openspp.org")
            self.assertEqual(data["message"], "Telemetry redirected to OpenSPP")
