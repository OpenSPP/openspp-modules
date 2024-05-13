from odoo.exceptions import ValidationError

from .common import Common


class TestSppApiFieldPath(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_get_path = cls.env["spp_api.path"].create(
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
                            cls.env.ref("base.field_res_partner__write_date").id,
                        ],
                    )
                ],
            }
        )
        cls.test_get_field_alias = cls.env["spp_api.field.alias"].create(
            {
                "field_id": cls.env.ref("base.field_res_partner__write_date").id,
                "alias_name": "last_updated",
                "api_path_id": cls.test_get_path.id,
            }
        )
        cls.test_post_path = cls.env["spp_api.path"].create(
            {
                "name": "res.partner",
                "model_id": cls.env.ref("base.model_res_partner").id,
                "namespace_id": cls.namespace_id.id,
                "description": "POST res.partner",
                "method": "post",
            }
        )
        cls.test_api_field = cls.env["spp_api.field"].create(
            {
                "field_id": cls.env.ref("base.field_res_partner__name").id,
                "required": True,
                "path_id": cls.test_post_path.id,
            }
        )
        cls.test_post_field_alias = cls.env["spp_api.field.alias"].create(
            {
                "field_id": cls.env.ref("base.field_res_partner__name").id,
                "alias_name": "fullname",
                "api_path_id": cls.test_post_path.id,
            }
        )

    def test_01_check_field_get_method(self):
        with self.assertRaisesRegex(ValidationError, "API need a specific fields list!"):
            self.test_get_path.write({"field_ids": [(5, 0, 0)]})

    def test_02_open_self_form(self):
        res = self.test_get_path.open_self_form()
        self.assertEqual(type(res), dict, "Return vals should be an action!")
        self.assertEqual(res["res_model"], "spp_api.path", "Return vals should be an action!")
        self.assertEqual(res["res_id"], self.test_get_path.id, "Return vals should be an action!")
        self.assertEqual(res["type"], "ir.actions.act_window", "Return vals should be an action!")

    def test_03_action_open_field_alias(self):
        res = self.test_get_path.action_open_field_alias()
        self.assertEqual(type(res), dict, "Return vals should be an action!")
        self.assertEqual(res["res_model"], "spp_api.field.alias", "Return vals should be an action!")
        self.assertEqual(
            res["context"].get("default_api_path_id"),
            self.test_get_path.id,
            "Return vals should be an action!",
        )
        self.assertEqual(res["type"], "ir.actions.act_window", "Return vals should be an action!")

    def test_04_fields_alias_treatment(self):
        res = self.test_post_path._fields_alias_treatment({"fullname": "Name 1", "age": 11})
        self.assertIn("name", res.keys(), "Post values should be treated correctly!")
        self.assertNotIn("fullname", res.keys(), "Post values should be treated correctly!")
        self.assertEqual(res["name"], "Name 1", "Post values should be treated correctly!")

    def test_05_get_response_treatment(self):
        res = self.test_get_path._get_response_treatment({"name": "Name", "write_date": "2023-11-13 13:12:00"})
        self.assertEqual(type(res), list, "Get values should be treated correctly!")
        for element in res:
            self.assertEqual(type(element), dict, "Get values should be treated correctly!")
            self.assertIn(
                "last_updated",
                element.keys(),
                "Get values should be treated correctly!",
            )
            self.assertNotIn("write_date", element.keys(), "Get values should be treated correctly!")
            self.assertEqual(
                element["last_updated"],
                "2023-11-13 13:12:00",
                "Get values should be treated correctly!",
            )
