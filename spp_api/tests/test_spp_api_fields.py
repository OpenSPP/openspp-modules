from .common import Common


class TestSppApiFields(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_path = cls.env["spp_api.path"].create(
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
                "path_id": cls.test_path.id,
            }
        )
        cls.test_field_alias = cls.env["spp_api.field.alias"].create(
            {
                "field_id": cls.env.ref("base.field_res_partner__name").id,
                "alias_name": "fullname",
                "api_path_id": cls.test_path.id,
            }
        )

    def test_01_create_api_field_name_alias(self):
        res = self.test_api_field.create_api_field_name_alias()
        self.assertTrue(isinstance(res, dict), "Return vals should be an action!")

    def test_02_get_field_name(self):
        res = self.test_api_field._get_field_name()
        self.assertEqual(res, "fullname", "Field should return field name alias!")
        self.test_field_alias.unlink()
        res = self.test_api_field._get_field_name()
        self.assertEqual(res, "name", "Field should return field name!")
