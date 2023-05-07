import json

from odoo import http
from odoo.tests import HttpCase

from odoo.addons.mail.tests.common import mail_new_test_user

from ..controllers.main import EXCEL_ROW_LIMIT


class TestSppExport(HttpCase):
    def setUp(self):
        super().setUp()
        queries = "INSERT INTO res_country_group (name) VALUES "
        values = []
        for i in range(EXCEL_ROW_LIMIT):
            values.append(f"('Test Country Group {i+1}')")
        queries += ",".join(values) + ";"
        self.env.cr.execute(queries)
        self.model = self.env["res.country.group"]
        mail_new_test_user(
            self.env,
            login="AgentSmith",
            password="GoodByeMrAnderson",
            groups="base.group_user,base.group_allow_export",
        )
        self.session = self.authenticate("AgentSmith", "GoodByeMrAnderson")

    def test_01_index(self):
        query_json = json.dumps(
            dict(
                {
                    "domain": [],
                    "fields": [
                        {"name": field.name, "label": field.string}
                        for field in self.model._fields.values()
                    ],
                    "groupby": [],
                    "ids": False,
                    "import_compat": False,
                    "model": self.model._name,
                }
            )
        )
        # Since controllers won't raise Errors like models,
        # we have to catch log to watch the errors raised
        with self.assertLogs(
            "odoo.addons.web.controllers.main", level="ERROR"
        ) as log_catcher:
            self.url_open(
                "/web/export/xlsx",
                data={
                    "data": query_json,
                    "token": "dummy",
                    "csrf_token": http.WebRequest.csrf_token(self),
                },
            )
            self.assertIn(
                "ValidationError", log_catcher.output[0], "Error should be raised"
            )
            self.assertIn(
                "surpasses the limitation of Excel",
                log_catcher.output[0],
                "Error should be raised",
            )
            self.assertIn(
                "Please consider splitting the export.",
                log_catcher.output[0],
                "Error should be raised",
            )
