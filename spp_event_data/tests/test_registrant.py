from .common import Common


class TestRegistrant(Common):
    def test_01_open_create_event_wizard(self):
        res = self._test_partner.open_create_event_wizard()
        self.assertEqual(
            res["res_model"],
            "spp.create.event.wizard",
            "open_create_event_wizard should give us the view of spp.create.event.wizard",
        )
