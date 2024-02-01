from .common import Common


class TestSppServicePointDevice(Common):
    def test_01_compute_name(self):
        self.assertEqual(
            self.test_devices[0].name,
            "Samsung A7-11 [ServicePoint1]",
            "Name should be computed correctly",
        )
        self.assertEqual(
            self.test_devices[1].name,
            "Sony Xperia5-14 [ServicePoint1]",
            "Name should be computed correctly",
        )

    def test_02_action_change_is_active(self):
        device = self.test_devices[0]
        self.assertTrue(device.is_active, "Is Active for device should be True as default")
        device.action_change_is_active()
        self.assertFalse(device.is_active, "Is Active for device should be changed")
        device.action_change_is_active()
        self.assertTrue(device.is_active, "Is Active for device should be changed")
