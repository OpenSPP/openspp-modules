from odoo.tests import TransactionCase

MODEL_NAME = "spp.event.agri.ds"


class TestEventDataAgriDS(TransactionCase):

    """
    Test for `spp.event.agri.ds` model.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._test_partner = cls.env["res.partner"].create(
            {
                "name": "FarmMates",
                "is_registrant": True,
                "is_group": True,
            }
        )

    def _mock_event_data_agri_ds(self):
        return self.env["spp.event.agri.ds"].create(
            {
                "survey_sched": "1",
            }
        )

    def create_mock_event_data(self):
        mock_event_data = self._mock_event_data_agri_ds()
        return self.env["spp.event.data"].create(
            {
                "partner_id": self._test_partner.id,
                "model": "spp.event.agri.ds",
                "res_id": mock_event_data.id,
            }
        )

    def test_01_mock_event_type(self):
        mock_event = self.create_mock_event()
        self.assertEqual(
            mock_event.model,
            "spp.event.agri.ds",
            "Mock event should have event type of `spp.event.agri.ds`!",
        )

    def test_02_mock_event_state(self):
        mock_event_1 = self.create_mock_event()
        mock_event_2 = self.create_mock_event()
        self.assertEqual(mock_event_1.state, "inactive", "Mock event 1 state should now ended!")
        self.assertEqual(mock_event_2.state, "active", "Mock event 2 state should now active!")

    def test_03_active_mock_event(self):
        mock_event_1 = self.create_mock_event()
        mock_event_2 = self.create_mock_event()
        self.assertEqual(
            self._test_partner._get_active_event_id(MODEL_NAME),
            mock_event_2.id,
            "Mock event 2 should be active event for test_partner!",
        )
        self.assertNotEqual(
            self._test_partner._get_active_event_id(MODEL_NAME),
            mock_event_1.id,
            "Mock event 1 should not be active event for test_partner!",
        )
        mock_event_3 = self.create_mock_event()
        self.assertEqual(
            self._test_partner._get_active_event_id(MODEL_NAME),
            mock_event_3.id,
            "Mock event 3 should be active event for test_partner!",
        )
        self.assertNotEqual(
            self._test_partner._get_active_event_id(MODEL_NAME),
            mock_event_2.id,
            "Mock event 2 should not be active event for test_partner!",
        )
