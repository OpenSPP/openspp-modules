from odoo.tests import TransactionCase


class TestIrModelFields(TransactionCase):
    def setUp(self):
        super().setUp()
        self.test_model = self.env["spp.test.daily.recompute.model"]
        self.test_field_1 = self.test_model._fields["field_to_test_1"]
        self.test_field_2 = self.test_model._fields["field_to_test_2"]
        self.test_field_3 = self.test_model._fields["field_to_test_3"]
        self.model_id = self.env.ref("spp_custom_field_recompute_daily.model_spp_test_daily_recompute_model").id

    def _create_test_record(self):
        return self.test_model.create(
            {
                "field_to_test_1": "101",
                "field_to_test_2": "202",
                "field_to_test_3": "303",
            }
        )

    def test_01_reflect_field_params(self):
        field_1_data = self.env["ir.model.fields"]._reflect_field_params(
            self.test_field_1,
            self.model_id,
        )
        self.assertTrue(
            field_1_data["recompute_daily"],
            "Field 1 should be recomputed daily as defined",
        )
        with self.assertLogs(
            "odoo.addons.spp_custom_field_recompute_daily.models.ir_model_fields",
            level="WARNING",
        ) as log_catcher:
            field_2_data = self.env["ir.model.fields"]._reflect_field_params(
                self.test_field_2,
                self.model_id,
            )
            self.assertFalse(
                field_2_data["recompute_daily"],
                "Field 2 should not be recomputed daily as defined [non-stored field]",
            )
            field_3_data = self.env["ir.model.fields"]._reflect_field_params(
                self.test_field_3,
                self.model_id,
            )
            self.assertFalse(
                field_3_data["recompute_daily"],
                "Field 3 should not be recomputed daily as defined [non-computed field]",
            )
            for warning in log_catcher.output:
                self.assertRegex(
                    warning,
                    r"Non-compute-stored field.*is not allowed to be recomputed daily!",
                    "Warning should be raised for Field 2 and Field 3!",
                )

    def test_02_recompute_indicator_on_records(self):
        test_record = self._create_test_record()
        test_field = self.env["ir.model.fields"].search([("recompute_daily", "=", True)])
        test_field._recompute_indicator_on_records(test_record)
        fields_to_compute = self.env.fields_to_compute()
        self.assertIn(
            self.test_field_1,
            fields_to_compute,
            "Field 1 should be marked as fields to compute in environment!",
        )

    def test_03_daily_recompute_indicators(self):
        self._create_test_record()
        self._create_test_record()
        self.env["ir.model.fields"]._daily_recompute_indicators()
        fields_to_compute = self.env.fields_to_compute()
        self.assertIn(
            self.test_field_1,
            fields_to_compute,
            "Field 1 should be marked as fields to compute in environment!",
        )
        recompute_indicator_jobs_count = self.env["queue.job"].search_count(
            [("func_string", "like", "_recompute_indicator_on_records")]
        )
        self.assertFalse(
            bool(recompute_indicator_jobs_count),
            "Jobs should not exists before reset max daily recompute " "record count and recompute indicators!",
        )
        self.env["ir.config_parameter"].set_param("spp.maximum_daily_recompute_count", "1")
        self.env["ir.model.fields"]._daily_recompute_indicators()
        recompute_indicator_jobs_count = self.env["queue.job"].search_count(
            [("func_string", "like", "_recompute_indicator_on_records")]
        )
        self.assertTrue(
            bool(recompute_indicator_jobs_count),
            "Jobs should exists after reset max daily recompute " "record count and recompute indicators!",
        )
