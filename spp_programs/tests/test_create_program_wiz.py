from odoo.tests import TransactionCase


class TestCreateProgramWiz(TransactionCase):
    def setUp(self):
        super().setUp()
        self.areas = self.env["spp.area"].create(
            [
                {"draft_name": "Area 1 [TEST]"},
                {"draft_name": "Area 2 [TEST]"},
                {"draft_name": "Area 3 [TEST]"},
            ]
        )
        self._program_create_wiz = self.env["g2p.program.create.wizard"].create(
            {
                "name": "Program 1 [TEST]",
                "rrule_type": "monthly",
                "eligibility_domain": "[]",
                "cycle_duration": 1,
                "currency_id": self.env.company.currency_id.id,
                "admin_area_ids": [(6, 0, self.areas.ids)],
                "amount_per_cycle": 1.0,
            }
        )

        self.program = self._program_create_wiz.create_program()
        # self.cycle_manager_default = (
        #     self._program_create_wiz.create_cycle_manager_default(self.program.id)
        # )

    def test_01_on_admin_area_ids_change(self):
        self.assertEqual(
            self._program_create_wiz.eligibility_domain,
            "[]",
            "Starting without eligibility domain!",
        )
        self._program_create_wiz.on_admin_area_ids_change()
        self.assertEqual(
            self._program_create_wiz.eligibility_domain,
            f"[('area_id', 'in', {tuple(self.areas.ids)})]",
            "Eligibility domain should be added!",
        )

    def test_02_create_program(self):
        # with self.assertRaisesRegex(
        #     UserError, "Amount per cycle.*Amount per individual in group"
        # ):
        #     self._program_create_wiz.create_program()
        self._program_create_wiz.amount_per_cycle = 5.0

        self._program_create_wiz.import_beneficiaries = "yes"
        res = self._program_create_wiz.create_program()
        self.assertEqual(type(res), dict, "Action should be in json format!")
        for key in ("type", "res_model", "res_id"):
            self.assertIn(key, res.keys(), f"Key `{key}` is missing!")
        self.assertEqual(
            res["type"],
            "ir.actions.act_window",
            "Action for program should be returned!",
        )
        self.assertEqual(res["res_model"], "g2p.program", "Action for program should be return!")
        self.assertTrue(res["res_id"], "New record for program should be existed!")

    def test_03_get_eligibility_manager(self):
        self._program_create_wiz.eligibility_kind = "default_eligibility"
        res = self._program_create_wiz._get_eligibility_manager(self.program["res_id"])

        self.assertIn("eligibility_managers", res)

    # def test_04_create_cycle_manager(self):
    #     cycle_manager = self._program_create_wiz.create_cycle_manager(
    #         self.program.id, self.cycle_manager_default
    #     )

    #     self.assertEqual(cycle_manager._name, "g2p.cycle.manager")
    #     self.assertIsNotNone(cycle_manager)

    # def test_05_create_cycle_manager_default(self):
    #     cycle_manager_default = self._program_create_wiz.create_cycle_manager_default(
    #         self.program.id
    #     )

    #     self.assertEqual(cycle_manager_default._name, "g2p.cycle.manager.default")
    #     self.assertIsNotNone(cycle_manager_default)

    def test_06_create_program(self):
        program = self._program_create_wiz.create_program()

        self.assertEqual(program["res_model"], "g2p.program")
        self.assertIsNotNone(program)
