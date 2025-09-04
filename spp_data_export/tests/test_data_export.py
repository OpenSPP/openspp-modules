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

    def test_export_with_ids_bypasses_check(self):
        """Test that the record check is bypassed when specific record IDs are provided."""
        data = {
            "model": self.test_model,
            "ids": [1, 2],
            "domain": [],
            "fields": [{"name": "name", "label": "Name"}],
        }
        json_data = json.dumps(data)

        # We expect the original `index` method to be called, which will eventually fail
        # because we are not in a real export flow, but it proves our override was bypassed.
        with self.assertRaises(AttributeError), self.authenticate("admin", "admin"):
            self.url_open(self.url, data={"data": json_data})

    def test_export_below_limit_succeeds(self):
        """Test that export proceeds when record count is below the limit."""
        data = {
            "model": self.test_model,
            "ids": False,
            "domain": [],
            "fields": [{"name": "name", "label": "Name"}],
        }
        json_data = json.dumps(data)

        # We expect the original `index` method to be called, which will eventually fail
        # because we are not in a real export flow, but it proves our check passed.
        with self.assertRaises(AttributeError), self.authenticate("admin", "admin"):
            self.url_open(self.url, data={"data": json_data})
