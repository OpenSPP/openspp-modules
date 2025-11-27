from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestPhoneValidation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model = cls.env["res.partner"]
        cls.phone_validation_model = cls.env["spp.phone.validation"]
        cls.phone_model = cls.env["g2p.phone.number"]
        cls.registrant = cls.partner_model.create(
            {
                "name": "Test Registrant",
                "is_registrant": True,
            }
        )
        cls.phone_validation_1 = cls.phone_validation_model.create(
            {
                "number_of_digits": 10,
                "with_prefix": True,
                "prefix": "+63",
                "state": "active",
            }
        )
        cls.phone_validation_2 = cls.phone_validation_model.create(
            {
                "number_of_digits": 11,
                "with_prefix": False,
                "state": "active",
            }
        )

    def test_01_create_phone_with_invalid_number(self):
        phone = self.phone_model.create(
            {
                "partner_id": self.registrant.id,
                "phone_no": "+639123456789",
                "country_id": self.env.ref("base.ph").id,
            }
        )

        with self.assertRaises(ValidationError) as cm:
            phone.phone_no = "12345"
            phone._onchange_phone_validation()

        self.assertIn("Phone number must match one of the following formats", str(cm.exception))

    def test_02_create_phone_with_valid_number_with_prefix(self):
        phone = self.phone_model.create(
            {
                "partner_id": self.registrant.id,
                "phone_no": "+639123456789",
                "country_id": self.env.ref("base.ph").id,
            }
        )
        phone._onchange_phone_validation()
        self.assertEqual(phone.phone_no, "+639123456789")

        phone = self.phone_model.create(
            {
                "partner_id": self.registrant.id,
                "phone_no": "+639-1234-56789",
                "country_id": self.env.ref("base.ph").id,
            }
        )
        phone._onchange_phone_validation()
        self.assertEqual(phone.phone_no, "+639-1234-56789")
        self.assertEqual(phone.phone_sanitized, "+639123456789")

    def test_03_create_phone_with_valid_number_without_prefix(self):
        phone = self.phone_model.create(
            {
                "partner_id": self.registrant.id,
                "phone_no": "09123456789",
                "country_id": self.env.ref("base.ph").id,
            }
        )
        phone._onchange_phone_validation()
        self.assertEqual(phone.phone_no, "09123456789")

    def test_04_create_phone_with_letters_in_number(self):
        phone_vals = {
            "partner_id": self.registrant.id,
            "phone_no": "09123A56789",
            "country_id": self.env.ref("base.ph").id,
        }
        with self.assertRaises(ValidationError) as cm:
            self.phone_model.create(phone_vals)

        self.assertIn("Phone number must not contain letters", str(cm.exception))

    def test_05_create_phone_with_invalid_special_characters(self):
        phone_vals = {
            "partner_id": self.registrant.id,
            "phone_no": "09123@456789",
            "country_id": self.env.ref("base.ph").id,
        }

        with self.assertRaises(ValidationError) as cm:
            self.phone_model.create(phone_vals)

        self.assertIn("Phone number contains invalid special characters", str(cm.exception))

    def test_06_activate_phone_validation(self):
        """Test activating a phone validation record"""
        phone_validation = self.phone_validation_model.create(
            {
                "number_of_digits": 9,
                "with_prefix": False,
                "state": "inactive",
            }
        )
        self.assertEqual(phone_validation.state, "inactive")

        phone_validation.activate_phone_validation()
        self.assertEqual(phone_validation.state, "active", "Phone validation state should be 'active' after activation")

    def test_07_deactivate_phone_validation(self):
        """Test deactivating a phone validation record"""
        phone_validation = self.phone_validation_model.create(
            {
                "number_of_digits": 8,
                "with_prefix": False,
                "state": "active",
            }
        )
        self.assertEqual(phone_validation.state, "active")

        phone_validation.deactivate_phone_validation()
        self.assertEqual(
            phone_validation.state, "inactive", "Phone validation state should be 'inactive' after deactivation"
        )
