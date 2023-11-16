from odoo.tests import TransactionCase


class TestSppApiFields(TransactionCase):
    def setUp(self):
        super().setUp()
        self.test_path = self.env["spp_api.path"].create(
            {
                "name": "res.partner",
                "model_id": self.env.ref("base.model_res_partner").id,
                "namespace_id": self.env.ref("spp_api.namespace_demo").id,
                "description": "POST res.partner",
                "method": "post",
            }
        )
        self.test_api_field = self.env["spp_api.field"].create(
            {
                "field_id": self.env.ref("base.field_res_partner__name").id,
                "required": True,
                "path_id": self.test_path.id,
            }
        )
        self.test_field_alias = self.env["spp_api.field.alias"].create(
            {
                "field_id": self.env.ref("base.field_res_partner__name").id,
                "alias_name": "fullname",
                "api_path_id": self.test_path.id,
            }
        )

    def test_01_create_api_field_name_alias(self):
        res = self.test_api_field.create_api_field_name_alias()
        self.assertTrue(type(res) == dict, "Return vals should be an action!")

    def test_02_get_field_name(self):
        res = self.test_api_field._get_field_name()
        self.assertEqual(res, "fullname", "Field should return field name alias!")
        self.test_field_alias.unlink()
        res = self.test_api_field._get_field_name()
        self.assertEqual(res, "name", "Field should return field name!")
