from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestIdType(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._default_id_type = cls.env.ref("spp_idpass.id_type_idpass")
        cls._non_default_id_type = cls.env["g2p.id.type"].create(
            {
                "name": "Test Id Type",
                "target_type": "individual",
            }
        )

    def test_01_write_default_id_type(self):
        new_name = "New Default ID Type"
        self._default_id_type.write(
            {
                "name": new_name,
            }
        )

        self.assertNotEqual(
            self._default_id_type.name,
            new_name,
            "Default Id Type should not be editable!",
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
        self.assertListEqual(test_id_type.ids, [], "Non-default Id Type should be deletable!")
