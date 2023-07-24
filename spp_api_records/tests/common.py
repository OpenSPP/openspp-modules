from odoo.tests import TransactionCase


class Common(TransactionCase):
    def setUp(self):
        super().setUp()
        self.service_point = self.env["spp.service.point"].create(
            {
                "name": "ServicePoint1",
                "phone_no": "+9647001234567",
                "is_disabled": False,
            }
        )
        self.test_devices = self.env["spp.service.point.device"].create(
            [
                {
                    "service_point_id": self.service_point.id,
                    "device_model": "Samsung A7",
                    "android_version": 11,
                    "service_point_terminal_device_id": "A7-11-1",
                },
                {
                    "service_point_id": self.service_point.id,
                    "device_model": "Sony Xperia5",
                    "android_version": 14,
                    "service_point_terminal_device_id": "X5-14-1",
                },
            ]
        )
