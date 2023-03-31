from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestIdType(TransactionCase):
    def setUp(self):
        super().setUp()
        self._default_id_type = self.env.ref("spp_idpass.id_type_idpass")
        self._non_default_id_type = self.env["g2p.id.type"].create(
            {
                "name": "Test Id Type",
                "target_type": "individual",
            }
        )

    def test_01_write_default_id_type(self):
        with self.assertRaises(ValidationError):
            self._default_id_type.write(
                {
                    "name": "1",
                }
            )

    def test_02_unlink_default_id_type(self):
        with self.assertRaises(ValidationError):
            self._default_id_type.unlink()

    def test_03_write_non_default_id_type(self):
        self._non_default_id_type.write(
            {
                "name": "1",
            }
        )
        self.assertEqual(
            self._non_default_id_type.name,
            "1",
            "Non-default Id Type should be editable!",
        )

    def test_04_unlink_non_default_id_type(self):
        self._non_default_id_type.unlink()
        test_id_type = self.env["g2p.id.type"].search([("name", "=", "Test Id Type")])
        self.assertListEqual(
            test_id_type.ids, [], "Non-default Id Type should be deletable!"
        )
