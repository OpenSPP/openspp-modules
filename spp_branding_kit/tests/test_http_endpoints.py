# ABOUTME: HttpCase tests for controller endpoints and session info

import json

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestBrandingHttp(HttpCase):
    def _jsonrpc(self, path, params=None):
        payload = {"jsonrpc": "2.0", "method": "call", "params": params or {}}
        resp = self.url_open(path, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        data = json.loads(resp.text)
        return data.get("result") if isinstance(data, dict) else data

    def test_version_info(self):
        result = self._jsonrpc("/web/webclient/version_info")
        self.assertIn("server_version", result)
        self.assertEqual(result["server_serie"], "17.0")

    def test_publisher_warranty_disabled(self):
        IrConfig = self.env["ir.config_parameter"].sudo()
        IrConfig.set_param("openspp.telemetry.enabled", "False")
        resp = self.url_open("/publisher-warranty")
        data = json.loads(resp.text)
        self.assertEqual(data.get("status"), "disabled")

    def test_publisher_warranty_enabled(self):
        IrConfig = self.env["ir.config_parameter"].sudo()
        IrConfig.set_param("openspp.telemetry.enabled", "True")
        IrConfig.set_param("openspp.telemetry.endpoint", "https://telemetry.openspp.org")
        resp = self.url_open("/publisher-warranty")
        data = json.loads(resp.text)
        self.assertEqual(data.get("status"), "redirected")
        self.assertTrue(data.get("endpoint"))

    def test_session_info_contains_branding(self):
        IrConfig = self.env["ir.config_parameter"].sudo()
        IrConfig.set_param("openspp.system.name", "OpenSPP Test")
        info = self._jsonrpc("/web/session/get_session_info")
        self.assertIn("openspp_system_name", info)
        self.assertEqual(info["openspp_system_name"], "OpenSPP Test")
        self.assertIn("server_version_info", info)
        self.assertEqual(info["server_version_info"][1], "17.0")
