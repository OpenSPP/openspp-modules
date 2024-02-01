from odoo import fields
from odoo.tests import TransactionCase


class TestSppApiNamespace(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._namespace = cls.env["spp_api.namespace"].create({"name": "test", "version_name": "v1"})
        cls.env["ir.config_parameter"].set_param("web.base.url", "https://local.host")
        cls._db_name = cls.env.cr.dbname

    # odoo17 name_get obsolete
    # def test_01_name_get(self):
    #     self.assertEqual(
    #         self._namespace.name_get(), [(self._namespace.id, "/api/test/v1")]
    #     )

    def test_02_compute_spec_url(self):
        token = self._namespace.token
        self.assertEqual(
            self._namespace.spec_url,
            f"https://local.host/api/test/v1/swagger.json?token={token}&db={self._db_name}",
        )
        self.assertEqual(
            self._namespace.spec_url_v2,
            f"https://local.host/api/swagger-doc/test/v1?token={token}&db={self._db_name}",
        )

    def test_03_reset_token(self):
        token = self._namespace.token
        self._namespace.reset_token()
        self.assertNotEqual(self._namespace.token, token)

    def test_04_fix_name(self):
        self._namespace.write({"name": "Test"})
        self.assertEqual(self._namespace.name, "test")

    def test_05_compute_log_count(self):
        self.assertEqual(self._namespace.log_count, 0)

    def test_06_compute_last_used(self):
        self.env["spp_api.log"].create(
            {
                "method": "get",
                "http_type": "request",
                "model": "res.partner",
                "namespace_id": self._namespace.id,
                "create_date": fields.Datetime.from_string("2023-11-24 00:00:00"),
            }
        )
        self.assertEqual(
            self._namespace.last_log_date,
            fields.Datetime.from_string("2023-11-24 00:00:00"),
        )
        self.env["spp_api.log"].create(
            {
                "method": "get",
                "http_type": "response",
                "model": "res.partner",
                "namespace_id": self._namespace.id,
                "create_date": fields.Datetime.from_string("2023-11-24 00:00:02"),
            }
        )
        self._namespace._compute_last_used()
        self.assertEqual(
            self._namespace.last_log_date,
            fields.Datetime.from_string("2023-11-24 00:00:02"),
        )

    def test_07_action_show_logs(self):
        res = self._namespace.action_show_logs()
        self.assertEqual(type(res), dict)
        for key in ["res_model", "type", "domain"]:
            self.assertIn(key, res.keys())
        self.assertEqual(res["type"], "ir.actions.act_window")
        self.assertEqual(res["res_model"], "spp_api.log")
        self.assertEqual(res["domain"], [["namespace_id", "=", self._namespace.id]])

    def test_08_get_oas(self):
        self.env["spp_api.path"].create(
            [
                {
                    "name": "res.partner",
                    "model_id": self.env.ref("base.model_res_partner").id,
                    "namespace_id": self._namespace.id,
                    "description": "GET res.partner",
                    "method": "get",
                    "field_ids": [
                        (
                            6,
                            0,
                            [
                                self.env.ref("base.field_res_partner__name").id,
                                self.env.ref("base.field_res_partner__write_date").id,
                            ],
                        ),
                    ],
                },
                {
                    "name": "res.partner",
                    "model_id": self.env.ref("base.model_res_partner").id,
                    "namespace_id": self._namespace.id,
                    "description": "POST res.partner",
                    "method": "post",
                    "api_field_ids": [
                        (
                            0,
                            0,
                            {
                                "field_id": self.env.ref("base.field_res_partner__name").id,
                            },
                        ),
                    ],
                },
                {
                    "name": "res.partner",
                    "model_id": self.env.ref("base.model_res_partner").id,
                    "namespace_id": self._namespace.id,
                    "description": "PUT res.partner",
                    "method": "put",
                    "api_field_ids": [
                        (
                            0,
                            0,
                            {
                                "field_id": self.env.ref("base.field_res_partner__name").id,
                            },
                        ),
                    ],
                },
                {
                    "name": "res.partner",
                    "model_id": self.env.ref("base.model_res_partner").id,
                    "namespace_id": self._namespace.id,
                    "description": "DELETE res.partner",
                    "method": "delete",
                },
                {
                    "name": "res.partner",
                    "model_id": self.env.ref("base.model_res_partner").id,
                    "namespace_id": self._namespace.id,
                    "description": "PATCH res.partner",
                    "method": "patch",
                },
            ]
        )
        with self.assertLogs(
            "odoo.addons.spp_api.models.spp_api_namespace",
            level="DEBUG",
        ) as log_catcher:
            self._namespace.get_oas(self._namespace.version_name)
            output = []
            for out in log_catcher.output:
                out = out.replace("DEBUG:odoo.addons.spp_api.models.spp_api_namespace:", "")
                output.append(out.split(":", 1)[0])
            self.assertEqual(output, ["path", "OAS_part_for_model", "spec"] * 5)
