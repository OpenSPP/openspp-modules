import json
from unittest.mock import patch

from odoo.exceptions import ValidationError
from odoo.tests.common import HttpCase

from odoo.addons.spp_data_export.controllers.main import EXCEL_ROW_LIMIT


class DataExportTest(HttpCase):
    @classmethod
    def setUpClass(cls):
        """
        Setup and create necessary records for this test
        """
        super().setUpClass()
        cls.env.user.groups_id |= cls.env.ref("base.group_system")
        cls.test_model = "res.partner"
        cls.url = "/web/export/xlsx"

    def test_01_export_with_ids_bypasses_check(self):
        """Test that the record check is bypassed when specific record IDs are provided for export."""
        self.authenticate("admin", "admin")
        with patch("odoo.addons.web.controllers.export.Export.index") as mock_super_index:
            mock_super_index.return_value = "Success"
            data = {
                "model": self.test_model,
                "ids": [1, 2],
                "domain": [],
                "fields": [{"name": "name", "label": "Name"}],
            }
            json_data = json.dumps(data)

            response = self.url_open(self.url, data={"data": json_data})
            self.assertEqual(response.text, "Success")
            mock_super_index.assert_called_once_with(json_data)

    def test_02_export_below_limit_succeeds(self):
        """Test that export proceeds when record count is below the limit."""
        self.authenticate("admin", "admin")
        with patch("odoo.addons.web.controllers.export.Export.index") as mock_super_index:
            mock_super_index.return_value = "Success"
            data = {
                "model": self.test_model,
                "ids": False,
                "domain": [],
                "fields": [{"name": "name", "label": "Name"}],
            }
            json_data = json.dumps(data)

            response = self.url_open(self.url, data={"data": json_data})
            self.assertEqual(response.text, "Success")
            mock_super_index.assert_called_once_with(json_data)

    def test_03_export_above_limit_fails(self):
        """Test that export fails with a ValidationError when record count is above the limit."""
        self.authenticate("admin", "admin")
        with patch("odoo.http.request.env") as mock_env, self.assertRaisesRegex(
            ValidationError, "The number of record surpasses the limitation"
        ):
            mock_env[self.test_model].sudo.return_value.search_count.return_value = EXCEL_ROW_LIMIT + 1
            data = {
                "model": self.test_model,
                "ids": False,
                "domain": [],
                "fields": [{"name": "name", "label": "Name"}],
            }
            json_data = json.dumps(data)

            self.url_open(self.url, data={"data": json_data})
            mock_env[self.test_model].sudo.return_value.search_count.assert_called_once_with([])
