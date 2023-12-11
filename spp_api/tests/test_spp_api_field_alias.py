from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase
from odoo.tools import mute_logger


class TestSppApiFieldAlias(TransactionCase):
    def setUp(self):
        super().setUp()
        self.test_path = self.env["spp_api.path"].create(
            {
                "name": "res.partner",
                "model_id": self.env.ref("base.model_res_partner").id,
                "namespace_id": self.env.ref("spp_api.namespace_demo").id,
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
                    )
                ],
            }
        )
        self.test_field_alias = self.env["spp_api.field.alias"].create(
            {
                "field_id": self.env.ref("base.field_res_partner__write_date").id,
                "alias_name": "last_updated",
                "api_path_id": self.test_path.id,
            }
        )

    def test_01_name_get(self):
        res = self.test_field_alias.name_get()[0][1]
        self.assertEqual(res, "last_updated - write_date")

    @mute_logger("py.warnings")
    def test_02_check_field_name_alias_name(self):
        with self.assertRaisesRegex(
            ValidationError, "Alias Name should be different from its field name!"
        ):
            self.test_field_alias.write({"alias_name": "write_date"})

    def test_03_inverse_global_alias(self):
        self.test_field_alias.write({"global_alias": True})
        self.assertFalse(bool(self.test_field_alias.api_path_id))

    def test_04_check_field_duplicate_if_api_path_is_null(self):
        self.test_field_alias.write({"global_alias": True})
        with self.assertRaisesRegex(
            ValidationError, "There is another global alias for this field!"
        ):
            self.env["spp_api.field.alias"].create(
                {
                    "field_id": self.env.ref("base.field_res_partner__write_date").id,
                    "alias_name": "last_updated",
                    "global_alias": True,
                }
            )
