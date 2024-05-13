from odoo.tests import TransactionCase

MODEL_NAME = "spp.event.hh.labor"


class TestEventDataHHLabor(TransactionCase):

    """
    Test for `spp.event.hh.labor` model.
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

    def _mock_event_data_type(self):
        return self.env[MODEL_NAME].create(
            {
                "survey_sched": "1",
            }
        )

    def create_mock_event_data(self):
        mock_event_data = self._mock_event_data_type()
        return self.env["spp.event.data"].create(
            {
                "partner_id": self._test_partner.id,
                "model": MODEL_NAME,
                "res_id": mock_event_data.id,
            }
        )

    def test_01_mock_event_type(self):
        mock_event = self.create_mock_event_data()
        self.assertEqual(
            mock_event.model,
            MODEL_NAME,
            ("Mock event should have event type of `%s`!", MODEL_NAME),
        )

    def test_02_mock_event_state(self):
        mock_event_1 = self.create_mock_event_data()
        mock_event_2 = self.create_mock_event_data()
        self.assertEqual(mock_event_1.state, "inactive", "Mock event 1 state should now ended!")
        self.assertEqual(mock_event_2.state, "active", "Mock event 2 state should now active!")

    def test_03_active_mock_event(self):
        mock_event_1 = self.create_mock_event_data()
        mock_event_2 = self.create_mock_event_data()
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
        mock_event_3 = self.create_mock_event_data()
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

    def test_04_active_mock_event_data(self):
        mock_event_1 = self.create_mock_event_data()
        mock_event_2 = self.create_mock_event_data()
        self._test_partner._compute_active_event_hh_labor()
        self.assertEqual(
            self._test_partner.active_event_hh_labor.id,
            mock_event_2.res_id,
            "Mock event 2 should be the active event data for test_partner!",
        )
        self.assertNotEqual(
            self._test_partner.active_event_hh_labor.id,
            mock_event_1.res_id,
            "Mock event 1 should not be the active event data for test_partner!",
        )
