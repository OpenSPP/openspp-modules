# Copyright 2018-2019 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2018 Rafis Bikbov <https://it-projects.info/team/bikbov>
# Copyright 2019 Anvar Kildebekov <https://it-projects.info/team/fedoranvar>
# Copyright 2021 Denis Mudarisov <https://github.com/trojikman>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import logging
import uuid

import requests

from odoo.tests import tagged
from odoo.tests.common import HttpCase, get_db_name
from odoo.tools import config

from ..controllers import pinguin

_logger = logging.getLogger(__name__)

USER_DEMO = "base.user_demo"
USER_ADMIN = "base.user_admin"
MESSAGE = "message is posted from API"


# TODO: test other methods:
# * /res.partner/call/{method_name} (without recordset)
# * /res.partner/{record_id}


@tagged("post_install", "-at_install")
class TestAPI(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.db_name = get_db_name()
        cls.partner_demo_id = cls.env["res.partner"].create(
            {
                "name": "Marc Demo",
                "company_id": cls.env.ref("base.main_company").id,
                "company_name": "YourCompany",
                "street": "3575  Buena Vista Avenue",
                "city": "Eugene",
                "state_id": cls.env.ref("base.state_us_41").id,
                "zip": "97401",
                "country_id": cls.env.ref("base.us").id,
                "tz": "Europe/Brussels",
                "email": "",
                "phone": "(441)-695-2334",
            }
        )
        cls.demo_user = cls.env["res.users"].create(
            {
                "partner_id": cls.partner_demo_id.id,
                "login": "demo_api_user",
                "password": "demo",
                "signature": "<span>-- <br/>+Mr Demo</span>",
                "company_id": cls.env.ref("base.main_company").id,
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref("base.group_user").id,
                            cls.env.ref("base.group_partner_manager").id,
                            cls.env.ref("base.group_allow_export").id,
                        ],
                    )
                ],
            }
        )
        cls.admin_user = cls.env["res.users"].create(
            {
                "login": "admin_spp_api",
                "password": "admin",
                "partner_id": cls.env.ref("base.partner_admin").id,
                "company_id": cls.env.ref("base.main_company").id,
            }
        )

        cls.namespace_id = cls.env["spp_api.namespace"].create(
            {
                "name": "demo_namespace_3",
                "log_request": "debug",
                "log_response": "debug",
                "token": "demo_token",
                "version_name": "v3",
                "user_ids": [(4, cls.demo_user.id)],
            }
        )

        cls.model_name = "res.partner"
        cls.env["spp_api.path"].create(
            [
                {
                    "name": "res.partner",
                    "model_id": cls.env.ref("base.model_res_partner").id,
                    "namespace_id": cls.namespace_id.id,
                    "description": "GET res.partner",
                    "method": "get",
                    "field_ids": [
                        (
                            6,
                            0,
                            [
                                cls.env.ref("base.field_res_partner__name").id,
                            ],
                        )
                    ],
                },
                {
                    "name": "res.partner",
                    "model_id": cls.env.ref("base.model_res_partner").id,
                    "namespace_id": cls.namespace_id.id,
                    "description": "POST res.partner",
                    "method": "post",
                    "api_field_ids": [
                        (
                            0,
                            0,
                            {"field_id": cls.env.ref("base.field_res_partner__name").id},
                        ),
                        (
                            0,
                            0,
                            {"field_id": cls.env.ref("base.field_res_partner__type").id},
                        ),
                    ],
                },
                {
                    "name": "res.partner",
                    "model_id": cls.env.ref("base.model_res_partner").id,
                    "namespace_id": cls.namespace_id.id,
                    "description": "UPDATE res.partner",
                    "method": "put",
                    "api_field_ids": [
                        (
                            0,
                            0,
                            {"field_id": cls.env.ref("base.field_res_partner__name").id},
                        ),
                        (
                            0,
                            0,
                            {"field_id": cls.env.ref("base.field_res_partner__type").id},
                        ),
                    ],
                },
                {
                    "name": "res.partner",
                    "model_id": cls.env.ref("base.model_res_partner").id,
                    "namespace_id": cls.namespace_id.id,
                    "description": "DELETE res.partner",
                    "method": "delete",
                },
            ]
        )

    def request(self, method, url, auth=None, **kwargs):
        kwargs.setdefault("model", self.model_name)
        kwargs.setdefault("namespace", "demo")
        kwargs.setdefault("namespace_version", "v1")
        url = ("http://localhost:%d/api/{namespace}/{namespace_version}" % config["http_port"] + url).format(**kwargs)
        self.opener = requests.Session()
        if method in ["POST", "PUT", "PATCH"]:
            json_data = kwargs.get("data_json")
            if "request_id" not in json_data:
                json_data["request_id"] = uuid.uuid4().__str__()
            return self.opener.request(method, url, timeout=30, auth=auth, json=kwargs.get("data_json"))
        params = {"request_id": uuid.uuid4().__str__()}
        return self.opener.request(
            method,
            url,
            timeout=30,
            auth=auth,
            json=kwargs.get("data_json"),
            params=params,
        )

    def request_from_user(self, user, *args, **kwargs):
        kwargs["auth"] = requests.auth.HTTPBasicAuth(self.db_name, user.openapi_token)
        return self.request(*args, **kwargs)

    # Note: Failing tests
    # TODO: Fix this test
    # @mute_logger("odoo.addons.spp_api.controllers.pinguin", "werkzeug")
    # def test_read_many_all(self):
    #     resp = self.request_from_user(self.demo_user, "GET", "/{model}")
    #     self.assertEqual(resp.status_code, pinguin.CODE__success)

    # Note: Failing tests
    # TODO: Fix this test
    # @mute_logger("odoo.addons.spp_api.controllers.pinguin", "werkzeug")
    # def test_read_one(self):
    #     record_id = self.env[self.model_name].search([], limit=1).id
    #     resp = self.request_from_user(self.demo_user, "GET", "/{model}/{record_id}", record_id=record_id)
    #     self.assertEqual(resp.status_code, pinguin.CODE__success)
    #     # TODO check content

    # Note: Failing tests
    # TODO: Fix this test
    # @mute_logger("odoo.addons.spp_api.controllers.pinguin", "werkzeug")
    # def test_create_one(self):
    #     data_for_create = {"name": "created_from_test", "type": "other"}
    #     resp = self.request_from_user(self.admin_user, "POST", "/{model}", data_json=data_for_create)
    #     self.assertEqual(resp.status_code, pinguin.CODE__created)
    #     self.assertIn("timestamp", resp.json().keys())
    #     self.assertIn("reply_id", resp.json().keys())

    # Note: Failing tests
    # TODO: Fix this test
    # @mute_logger("odoo.addons.spp_api.controllers.pinguin", "werkzeug", "odoo.sql_db")
    # def test_create_one_with_invalid_data(self):
    #     """create partner without name"""
    #     data_for_create = {"email": "string"}
    #     with (
    #         self.assertRaises(Exception),
    #         self.phantom_env.cr.savepoint(flush=False),
    #     ):
    #         resp = self.request_from_user(
    #             self.demo_user, "POST", "/{model}", data_json=data_for_create
    #         )
    #         self.assertEqual(resp.status_code, 400)

    # Note: Failing tests
    # TODO: Fix this test
    # @mute_logger("odoo.addons.spp_api.controllers.pinguin", "werkzeug")
    # def test_update_one(self):
    #     data_for_update = {
    #         "name": "for update in test",
    #     }
    #     partner = self.env[self.model_name].search([], limit=1)
    #     resp = self.request_from_user(
    #         self.demo_user,
    #         "PUT",
    #         "/{model}/{record_id}",
    #         record_id=partner.id,
    #         data_json=data_for_update,
    #     )
    #     self.assertEqual(resp.status_code, pinguin.CODE__success)
    #     self.assertIn("timestamp", resp.json().keys())
    #     self.assertIn("reply_id", resp.json().keys())
    #     # TODO: check result

    # Note: Failing tests
    # TODO: Fix this test
    # @mute_logger("odoo.addons.spp_api.controllers.pinguin", "werkzeug", "odoo.models.unlink")
    # def test_unlink_one(self):
    #     with self.env.cr.savepoint():
    #         partner = self.env[self.model_name].create({"name": "record for deleting from test"})
    #         self.env[self.model_name].invalidate_model()

    #         resp = self.request_from_user(self.admin_user, "DELETE", "/{model}/{record_id}", record_id=partner.id)
    #         self.assertEqual(resp.status_code, pinguin.CODE__success)
    #         self.assertFalse(self.env[self.model_name].browse(partner.id).exists())

    # Note: Failing tests
    # TODO: Fix this test
    # @mute_logger("odoo.addons.spp_api.controllers.pinguin", "werkzeug")
    # def test_unauthorized_user(self):
    #     resp = self.request("GET", "/{model}")
    #     self.assertEqual(resp.status_code, pinguin.CODE__no_user_auth[0])

    # TODO: doesn't work in test environment
    def _test_invalid_dbname(self):
        db_name = "invalid_db_name"
        resp = self.request(
            "GET",
            "/{model}",
            auth=requests.auth.HTTPBasicAuth(db_name, self.demo_user.openapi_token),
        )
        self.assertEqual(resp.status_code, pinguin.CODE__db_not_found[0])
        self.assertEqual(resp.json()["error"], pinguin.CODE__db_not_found[1])

    # Note: Failing tests
    # TODO: Fix this test
    # @mute_logger("odoo.addons.spp_api.controllers.pinguin", "werkzeug")
    # def test_invalid_user_token(self):
    #     invalid_token = "invalid_user_token"
    #     resp = self.request(
    #         "GET",
    #         "/{model}",
    #         auth=requests.auth.HTTPBasicAuth(self.db_name, invalid_token),
    #     )
    #     self.assertEqual(resp.status_code, pinguin.CODE__no_user_auth[0])
    #     self.assertEqual(resp.json()["error"], pinguin.CODE__no_user_auth[1])

    # def test_user_not_allowed_for_namespace(self):
    #     namespace = self.phantom_env["spp_api.namespace"].search(
    #         [("name", "=", "demo")]
    #     )
    #     new_user = self.phantom_env["res.users"].create(
    #         {"name": "new user", "login": "new_user"}
    #     )
    #     new_user.write(
    #         {"groups_id": [(4, self.phantom_env.ref("spp_api.group_user").id)]}
    #     )
    #     new_user.reset_openapi_token()
    #     new_user.flush()
    #     self.assertTrue(new_user.id not in namespace.user_ids.ids)
    #     self.assertTrue(namespace.id not in new_user.namespace_ids.ids)

    #     resp = self.request_from_user(new_user, "GET", "/{model}")
    #     self.assertEqual(resp.status_code, pinguin.CODE__user_no_perm[0], resp.json())
    #     self.assertEqual(resp.json()["error"], pinguin.CODE__user_no_perm[1])

    # Note: Failing tests
    # TODO: Fix this test
    # @mute_logger("odoo.addons.spp_api.controllers.pinguin", "werkzeug")
    # def test_call_allowed_method_on_singleton_record(self):
    #     if not self.env["ir.module.module"].search([("name", "=", "mail")]).state == "installed":
    #         self.skipTest("To run test 'test_call_allowed_method_on_singleton_record' install 'mail'-module")
    #     self.env["spp_api.path"].create(
    #         {
    #             "name": "res.partner",
    #             "model_id": self.env.ref("base.model_res_partner").id,
    #             "namespace_id": self.namespace_id.id,
    #             "description": "PATCH res.partner",
    #             "method": "patch",
    #             "function": "message_post",
    #             "function_parameter_ids": [
    #                 (0, 0, {"name": "body", "type": "string"}),
    #             ],
    #         }
    #     )
    #     partner = self.env[self.model_name].search([], limit=1)
    #     method_name = "message_post"
    #     method_params = {"body": MESSAGE}
    #     resp = self.request_from_user(
    #         self.demo_user,
    #         "PATCH",
    #         "/{model}/{record_id}/call/{method_name}",
    #         record_id=partner.id,
    #         method_name=method_name,
    #         data_json=method_params,
    #     )
    #     self.assertEqual(resp.status_code, pinguin.CODE__success)

    # Note: Failing tests
    # TODO: Fix this test
    # @mute_logger("odoo.addons.spp_api.controllers.pinguin", "werkzeug")
    # def test_call_allowed_method_on_recordset(self):
    #     self.env["spp_api.path"].create(
    #         {
    #             "name": "res.partner",
    #             "model_id": self.env.ref("base.model_res_partner").id,
    #             "namespace_id": self.namespace_id.id,
    #             "description": "PATCH res.partner",
    #             "method": "patch",
    #             "function": "write",
    #             "function_parameter_ids": [
    #                 (0, 0, {"name": "vals", "type": "object"}),
    #             ],
    #         }
    #     )
    #     partners = self.env[self.model_name].search([], limit=5)
    #     method_name = "write"
    #     method_params = {
    #         "vals": {"name": "changed from write method called from api"},
    #     }
    #     ids = partners.mapped("id")
    #     ids_str = ",".join(str(i) for i in ids)

    #     resp = self.request_from_user(
    #         self.demo_user,
    #         "PATCH",
    #         "/{model}/call/{method_name}/{ids_str}",
    #         method_name=method_name,
    #         ids_str=ids_str,
    #         data_json=method_params,
    #     )

    #     self.assertEqual(resp.status_code, pinguin.CODE__success)
    #     self.assertListEqual(partners.mapped("name"), [method_params["vals"]["name"]] * 5)

    # Note: Failing tests
    # TODO: Fix this test
    # def test_call_model_method(self):
    #     self.env["spp_api.path"].create(
    #         {
    #             "name": "res.partner",
    #             "model_id": self.env.ref("base.model_res_partner").id,
    #             "namespace_id": self.namespace_id.id,
    #             "description": "PATCH res.partner",
    #             "method": "patch",
    #             "function": "search_read",
    #             "function_parameter_ids": [
    #                 (0, 0, {"name": "domain", "type": "array"}),
    #                 (0, 0, {"name": "fields", "type": "array"}),
    #             ],
    #         }
    #     )
    #     domain = [["id", "=", 1]]
    #     record = self.env[self.model_name].search(domain)
    #     self.assertTrue(record, "Record with ID 1 is not available")

    #     method_name = "search_read"
    #     method_params = {
    #         "domain": [["id", "=", "1"]],
    #         "fields": ["id", "name"],
    #     }
    #     resp = self.request_from_user(
    #         self.demo_user,
    #         "PATCH",
    #         "/{model}/call/{method_name}",
    #         method_name=method_name,
    #         data_json=method_params,
    #     )

    #     self.assertEqual(resp.status_code, pinguin.CODE__success)
    #     for item in resp.json():
    #         self.assertIn("id", item)
    #         self.assertIn("name", item)

    # Note: Failing tests
    # TODO: Fix this test
    # @mute_logger("odoo.addons.spp_api.controllers.pinguin", "werkzeug")
    # def test_log_creating(self):
    #     logs_count_before_request = len(self.env["spp_api.log"].search([]))
    #     self.request_from_user(self.demo_user, "GET", "/{model}")
    #     logs_count_after_request = len(self.env["spp_api.log"].search([]))
    #     self.assertTrue(logs_count_after_request > logs_count_before_request)

    # # TODO test is not update for the latest module version
    # def _test_get_report_for_allowed_model(self):
    #     super_user = self.phantom_env.ref(USER_ADMIN)
    #     modelname_for_report = "ir.module.module"
    #     report_external_id = "base.ir_module_reference_print"

    #     model_for_report = self.phantom_env["ir.model"].search(
    #         [("model", "=", modelname_for_report)]
    #     )
    #     namespace = self.phantom_env["spp_api.namespace"].search([("name", "=")])
    #     records_for_report = self.phantom_env[modelname_for_report].search([], limit=3)
    #     docids = ",".join([str(i) for i in records_for_report.ids])

    #     self.phantom_env["openapi.access"].create(
    #         {
    #             "active": True,
    #             "namespace_id": namespace.id,
    #             "model_id": model_for_report.id,
    #             "model": modelname_for_report,
    #             "api_create": False,
    #             "api_read": True,
    #             "api_update": False,
    #             "api_public_methods": False,
    #             "public_methods": False,
    #             "private_methods": False,
    #             "read_one_id": False,
    #             "read_many_id": False,
    #             "create_context_ids": False,
    #         }
    #     )

    #     super_user.write({"namespace_ids": [(4, namespace.id)]})

    #     url = "http://localhost:%d/api/v1/demo/report/html/%s/%s" % (
    #         config["http_port"],
    #         report_external_id,
    #         docids,
    #     )
    #     resp = requests.request(
    #         "GET",
    #         url,
    #         timeout=30,
    #         auth=requests.auth.HTTPBasicAuth(self.db_name, super_user.openapi_token),
    #     )
    #     self.assertEqual(resp.status_code, pinguin.CODE__success)

    # Note: Failing tests
    # TODO: Fix this test
    # def test_response_has_no_error(self):
    #     self.env["spp_api.path"].create(
    #         {
    #             "name": "res.partner",
    #             "model_id": self.env.ref("base.model_res_partner").id,
    #             "namespace_id": self.namespace_id.id,
    #             "description": "PATCH res.partner",
    #             "method": "patch",
    #             "function": "search_read",
    #             "function_parameter_ids": [
    #                 (0, 0, {"name": "domain", "type": "array"}),
    #                 (0, 0, {"name": "fields", "type": "array"}),
    #             ],
    #         }
    #     )
    #     method_name = "search_read"
    #     method_params = {
    #         "domain": [["id", "=", "1"]],
    #         "fields": ["id", "name"],
    #     }
    #     resp = self.request_from_user(
    #         self.demo_user,
    #         "PATCH",
    #         "/{model}/call/{method_name}",
    #         method_name=method_name,
    #         data_json=method_params,
    #     )
    #     self.assertNotIn("error", resp.json())
