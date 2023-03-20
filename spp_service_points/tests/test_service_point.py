from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestServicePoint(TransactionCase):
    def setUp(self):
        super().setUp()
        country = self.env.ref("base.iq")
        self.service_point_1 = self.env["spp.service.point"].create(
            {
                "name": "Correct Phone Number",
                "country_id": country.id,
                "phone_no": "+9647001234567",
                "is_disabled": False,
            }
        )
        self.service_point_2 = self.env["spp.service.point"].create(
            {
                "name": "In-correct Phone Number",
                "country_id": country.id,
                "phone_no": "+964700123456",
                "is_disabled": True,
                "disabled_reason": "Wrong phone number format!",
            }
        )

    def test_01_correct_phone_sanitized(self):
        self.assertNotEqual(
            self.service_point_1.phone_sanitized,
            False,
            "Service Point 1 having correct Iraq phone number format, should have phone sanitized!",
        )

    def test_02_incorrect_phone_sanitized(self):
        self.assertEqual(
            self.service_point_2.phone_sanitized,
            "False",
            "Service Point 2 having in-correct Iraq phone number format, should not have phone sanitized!",
        )

    def test_03_disable_active_service_point(self):
        self.service_point_1.disable_service_point()
        self.assertEqual(
            self.service_point_1.is_disabled,
            True,
            "Service Point 1 should be disable after disabling!",
        )
        self.assertEqual(
            self.service_point_1.disabled_date,
            fields.Date.today(),
            "Service Point 1 should be disable today!",
        )

    def test_04_disable_inactive_service_point(self):
        with self.assertRaises(UserError):
            self.service_point_2.disable_service_point()

    def test_05_enable_service_point(self):
        self.service_point_2.enable_service_point()
        self.assertFalse(
            self.service_point_2.is_disabled,
            "Service Point 2 should be enable after enabling!",
        )
        self.assertFalse(
            self.service_point_2.disabled_date,
            "Service Point 2 should be enable after enabling!",
        )
        self.assertFalse(
            self.service_point_2.disabled_reason,
            "Service Point 2 should be enable after enabling!",
        )

    def test_06_enable_service_point(self):
        with self.assertRaises(UserError):
            self.service_point_1.enable_service_point()
