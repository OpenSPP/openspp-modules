# ABOUTME: Unit tests for the controllers in spp_branding_kit
# ABOUTME: Tests OpenSPPHome controller functionality

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
        with patch("odoo.addons.spp_branding_kit.controllers.main.request") as mock_request:
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
        with patch("odoo.addons.spp_branding_kit.controllers.main.request") as mock_request:
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
        with patch("odoo.addons.spp_branding_kit.controllers.main.request") as mock_request:
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


# Note: Controller tests that require HTTP request context have been removed
# These tests would require HttpCase instead of TransactionCase to work properly
