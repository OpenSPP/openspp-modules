from .common import Common


class TestEntitlementReportWiz(Common):
    def setUp(self):
        super().setUp()
        self._test_record = self.env["g2p.entitlement.inkind.report.wizard"].create(
            {
                "cycle_id": self.cycle.id,
                "program_id": self.program.id,
            }
        )

    def test_01_compute_cycle_id_domain(self):
        self._test_record._compute_cycle_id_domain()
        self.assertEqual(
            self._test_record.cycle_id_domain,
            f'[["program_id", "=", {self.program.id}]]',
            "Cycle Domain should be correct!",
        )

    def test_02_generate_report(self):
        res = self._test_record.generate_report()
        self.assertEqual(type(res), dict, "Action should be return as a dictionary!")
        for key in ["res_model", "domain", "type", "flags"]:
            self.assertIn(key, res.keys(), f"> `{key}` should be in return action!")
        self.assertEqual(res["res_model"], "g2p.entitlement.inkind", "Should return correct model!")
        self.assertEqual(
            res["domain"],
            [("program_id", "=", self.program.id), ("cycle_id", "=", self.cycle.id)],
            "Should return correct domain!",
        )
        self.assertEqual(res["type"], "ir.actions.act_window", "Should return action window!")
        self.assertEqual(res["flags"], {"mode": "readonly"}, "Should be readonly action!")
