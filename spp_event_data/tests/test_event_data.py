from ..models.registrant import OpenSPPRegistrant
from .common import Common


class TestEventData(Common):
    def setUp(self):
        super().setUp()
        self._test_partner = self.env["res.partner"].create(
            {
                "name": "Cao Cao",
                "is_registrant": True,
            }
        )

    def create_mock_event(self):
        return self.env["spp.event.data"].create(
            {
                "partner_id": self._test_partner.id,
                "model": "res.partner",
                "res_id": self._test_partner.id,
            }
        )

    def test_01_mock_event_type(self):
        mock_event = self.create_mock_event()
        self.assertEqual(
            mock_event.event_type,
            "Contact",
            "Mock event should have event type of `Contact`!",
        )

    def test_02_mock_event_state(self):
        mock_event_1 = self.create_mock_event()
        mock_event_2 = self.create_mock_event()
        self.assertEqual(
            mock_event_1.state, "inactive", "Mock event 1 state should now ended!"
        )
        self.assertEqual(
            mock_event_2.state, "active", "Mock event 2 state should now active!"
        )

    def test_03_active_mock_even(self):
        mock_event_1 = self.create_mock_event()
        mock_event_2 = self.create_mock_event()
        self.assertEqual(
            self._test_partner._get_active_event_id(self._test_partner._name),
            mock_event_2.id,
            "Mock event 2 should be active event for test_partner!",
        )
        self.assertNotEqual(
            self._test_partner._get_active_event_id(self._test_partner._name),
            mock_event_1.id,
            "Mock event 1 should not be active event for test_partner!",
        )
        mock_event_3 = self.create_mock_event()
        self.assertEqual(
            self._test_partner._get_active_event_id(self._test_partner._name),
            mock_event_3.id,
            "Mock event 3 should be active event for test_partner!",
        )
        self.assertNotEqual(
            self._test_partner._get_active_event_id(self._test_partner._name),
            mock_event_2.id,
            "Mock event 2 should not be active event for test_partner!",
        )

    def test_04_open_form(self):
        OpenSPPRegistrant.get_view_id = lambda rec: 1
        mock_event = self.create_mock_event()
        res = mock_event.open_form()
        self.assertEqual(
            res["res_model"], "res.partner", "open_form should give us correct model"
        )
        self.assertEqual(
            res["res_id"],
            self._test_partner.id,
            "open_form should give us correct record id",
        )
        self.assertFalse(
            res["context"]["create"],
            "Should not allow user to create new record in next action",
        )
        self.assertFalse(
            res["context"]["edit"],
            "Should not allow user to edit record in next action",
        )
