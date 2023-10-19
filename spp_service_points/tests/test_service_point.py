from odoo import _, fields
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

        self.res_partner_company = self.env["res.partner"].create(
            {
                "name": "company_test",
                "is_company": True,
            }
        )

        self.res_partner_company_2 = self.env["res.partner"].create(
            {
                "name": "company_test",
                "is_company": True,
            }
        )

        self.res_partner_individual = self.env["res.partner"].create(
            {
                "name": "individual_test",
                "parent_id": self.res_partner_company.id,
            }
        )

        self.res_partner_individual_2 = self.env["res.partner"].create(
            {
                "name": "individual_test_2",
                "email": "individual_test_2@ymail.com",
            }
        )

        self.service_point_3 = self.env["spp.service.point"].create(
            {
                "name": "Without Company",
                "country_id": country.id,
                "phone_no": "+964700123456",
            }
        )

        self.service_point_4 = self.env["spp.service.point"].create(
            {
                "name": "With Company and Contacts",
                "country_id": country.id,
                "res_partner_company_id": self.res_partner_company.id,
            }
        )

        self.service_point_5 = self.env["spp.service.point"].create(
            {
                "name": "With Company and without Contacts",
                "country_id": country.id,
                "res_partner_company_id": self.res_partner_company_2.id,
            }
        )

    def test_01_correct_phone_sanitized(self):
        self.assertNotEqual(
            self.service_point_1.phone_sanitized,
            False,
            "Service Point 1 having correct Iraq phone number format, should have phone sanitized!",
        )

    def test_02_disable_active_service_point(self):
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

    def test_03_disable_inactive_service_point(self):
        with self.assertRaises(UserError):
            self.service_point_2.disable_service_point()

    def test_04_enable_service_point(self):
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

    def test_05_enable_service_point(self):
        with self.assertRaises(UserError):
            self.service_point_1.enable_service_point()

    def test_06_create_user(self):
        with self.assertRaisesRegex(UserError, "Service point does not have company."):
            self.service_point_3.create_user()

        with self.assertRaisesRegex(UserError, "Company does not have contacts."):
            self.service_point_5.create_user()

        expected_result = {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Create SP User"),
                "message": _(
                    "Successfully created users for the contacts of the company"
                ),
                "sticky": True,
                "type": "success",
                "next": {
                    "type": "ir.actions.act_window_close",
                },
            },
        }

        with self.assertRaisesRegex(
            UserError, f"{self.res_partner_individual.name} does not have email."
        ):
            self.service_point_4.create_user()

        self.res_partner_individual.email = "test_indv@ymail.com"

        self.assertEqual(self.service_point_4.create_user(), expected_result)

        self.assertIsNotNone(self.res_partner_individual.user_ids)

        self.res_partner_individual_2.parent_id = self.res_partner_company.id

        user = self.service_point_4._create_user(self.res_partner_individual_2)

        self.assertIsNotNone(user)
