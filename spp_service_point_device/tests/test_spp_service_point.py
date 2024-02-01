from .common import Common


class TestSppServicePoint(Common):
    def test_01_action_view_terminal_devices(self):
        res = self.service_point.action_view_terminal_devices()
        self.assertEqual(type(res), dict, "Return type should be json action")
        self.assertEqual(res.get("type"), "ir.actions.act_window", "Should return action window")
        self.assertEqual(
            res.get("res_model"),
            "spp.service.point.device",
            "Should call terminal device model",
        )
        self.assertEqual(
            res.get("domain"),
            [("service_point_id", "=", self.service_point.id)],
            "Should show for 1 service point only",
        )
