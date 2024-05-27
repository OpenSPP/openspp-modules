from odoo.tests import TransactionCase


class TestGenerateFarmerData(TransactionCase):

    """
    Test for `spp.laos.generate.farmer.data` model.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._test_generate_data = cls.env["spp.laos.generate.farmer.data"].create(
            {"name": "MockGenerateData", "num_groups": 10}
        )

        cls._test_generate_data.generate_sample_data()

    def test_01_check_status(self):
        self.assertEqual(
            self._test_generate_data.state,
            "generate",
            "Mock Data Generation should be generated!",
        )

    def test_02_check_total_farmer_groups_created(self):
        total_groups_created = len(
            self.env["res.partner"].search(
                [
                    ("is_group", "=", True),
                    ("is_registrant", "=", True),
                    ("kind", "=", self.env.ref("spp_farmer_registry_laos.kind_farmer_group").id),
                ]
            )
        )
        self.assertEqual(
            self._test_generate_data.num_groups,
            total_groups_created,
            "Total Number of Farmer Groups doesn't match with the number of groups!",
        )

    def test_03_check_event_datas(self):
        farmer_group = self.env["res.partner"].search(
            [
                ("is_group", "=", True),
                ("is_registrant", "=", True),
                ("kind", "=", self.env.ref("spp_farmer_registry_laos.kind_farmer_group").id),
            ],
            limit=1,
        )
        self.assertNotEqual(farmer_group.active_event_agri_ds, False, "No active_event_agri_ds found!")
        self.assertNotEqual(farmer_group.active_event_agri_ds_hot, False, "No active_event_agri_ds_hot found!")
        self.assertNotEqual(
            farmer_group.active_event_agri_land_ownership_use, False, "No active_event_agri_land_ownership_use found!"
        )
        self.assertNotEqual(farmer_group.active_event_agri_ws, False, "No active_event_agri_ws found!")
        self.assertNotEqual(farmer_group.active_event_food_security, False, "No active_event_food_security found!")
        self.assertNotEqual(farmer_group.active_event_gen_info, False, "No active_event_gen_info found!")
        self.assertNotEqual(farmer_group.active_event_hh_assets, False, "No active_event_hh_assets found!")
        self.assertNotEqual(farmer_group.active_event_hh_labor, False, "No active_event_hh_labor found!")
        self.assertNotEqual(
            farmer_group.active_event_hh_resilience_index, False, "No active_event_hh_resilience_index found!"
        )
        self.assertNotEqual(farmer_group.active_event_inc_agri, False, "No active_event_inc_agri found!")
        self.assertNotEqual(farmer_group.active_event_inc_non_agri, False, "No active_event_inc_non_agri found!")
        self.assertNotEqual(
            farmer_group.active_event_livestock_farming, False, "No active_event_livestock_farming found!"
        )
        self.assertNotEqual(
            farmer_group.active_event_min_dietary_score, False, "No active_event_min_dietary_score found!"
        )
        self.assertNotEqual(farmer_group.active_event_permanent_crops, False, "No active_event_permanent_crops found!")
        self.assertNotEqual(
            farmer_group.active_event_poverty_indicator, False, "No active_event_poverty_indicator found!"
        )
        self.assertNotEqual(farmer_group.active_event_cycle, False, "No active_event_cycle found!")
        self.assertNotEqual(farmer_group.active_event_wash_ind, False, "No active_event_wash_ind found!")
