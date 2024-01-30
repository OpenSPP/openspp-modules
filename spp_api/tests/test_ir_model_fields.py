from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestIrModelFields(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_path = cls.env["spp_api.path"].create(
            {
                "name": "res.partner",
                "model_id": cls.env.ref("base.model_res_partner").id,
                "namespace_id": cls.env.ref("spp_api.namespace_demo").id,
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
        cls.test_field_alias = cls.env["spp_api.field.alias"].create(
            {
                "field_id": cls.env.ref("base.field_res_partner__write_date").id,
                "alias_name": "last_updated",
                "api_path_id": cls.test_path.id,
            }
        )

    def test_01_create_api_field_name_alias(self):
        test_field_name = self.env.ref("base.field_res_partner__name")
        test_field_write_date = self.env.ref("base.field_res_partner__write_date")
        with self.assertRaisesRegex(ValidationError, "API path is not specify!"):
            test_field_name.create_api_field_name_alias()
        res = test_field_name.with_context(
            default_api_path_id=self.test_path.id
        ).create_api_field_name_alias()
        self.assertTrue(type(res) == dict, "Return values should be an action!")
        self.assertFalse(bool(res.get("res_id")), "Name doesn't have its field alias!")
        res = test_field_write_date.with_context(
            default_api_path_id=self.test_path.id
        ).create_api_field_name_alias()
        self.assertTrue(
            bool(res.get("res_id")), "Write date has field alias, it should be shown!"
        )
