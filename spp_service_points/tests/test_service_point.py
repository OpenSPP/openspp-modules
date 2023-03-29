from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class OpenSPPServicePointTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.center_area = cls.env["spp.area"].create(
            {
                "code": "my-code",
                "draft_name": "my-draft-name",
            }
        )

        cls.service_point = cls.env["spp.service.point"].create(
            {
                "name": "Agent Test",
                "area_id": cls.center_area.id,
            }
        )

        cls.service_point = cls.env["spp.service.point"].create(
            {"name": "Agent Red", "is_disabled": True, "area_id": cls.center_area.id}
        )

    def test_disable_service_point(self):
        with self.assertRaises(UserError):
            self.service_point.disable_service_point()

        self.service_point.is_disabled = False
        self.service_point.disable_service_point()

        self.assertEqual(self.service_point.is_disabled, True)

    def test_enable_service_point(self):
        self.service_point.is_disabled = False

        with self.assertRaises(UserError):
            self.service_point.enable_service_point()

        self.service_point.is_disabled = True
        self.service_point.enable_service_point()

        self.assertEqual(self.service_point.is_disabled, False)
        self.assertEqual(self.service_point.disabled_date, False)
        self.assertEqual(self.service_point.disabled_reason, False)
