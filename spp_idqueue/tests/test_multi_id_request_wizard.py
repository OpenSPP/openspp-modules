from datetime import date

from odoo.exceptions import UserError

from .common import Common


class TestMultiIdRequestWizard(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._model = cls.env["spp.multi.id.request.wizard"]
        cls._target_model = cls.env["spp.print.queue.id"]
        cls.all_individual = cls._test_individual_1 | cls._test_individual_2 | cls._test_individual_3

    def _create_correct_multi_id_request_wizard(self):
        wiz = self._model.with_context(active_ids=self.all_individual.ids).create(
            {
                "id_type": self.env.ref("spp_idpass.id_type_idpass").id,
            }
        )
        wiz._onchange_template()
        return wiz

    def test_01_compute_target_type_no_members(self):
        with self.assertRaises(UserError):
            self._model.create({})

    def test_02_compute_target_type(self):
        individual_target = self._create_correct_multi_id_request_wizard()
        group_target = self._model.with_context(active_ids=self._test_group.ids).create({})
        self.assertEqual(
            individual_target.target_type,
            "individual",
            "Test data should have target type of `individual`!",
        )
        self.assertEqual(
            group_target.target_type,
            "group",
            "Test data should have target type of `group`!",
        )

    def test_03_onchange_template(self):
        wiz = self._create_correct_multi_id_request_wizard()
        self.assertTrue(wiz.is_idpass, "Id Type should be ID Pass!")

    def test_04_create_requests_no_id_type(self):
        wiz = self._model.with_context(active_ids=self._test_group.ids).create({})
        with self.assertRaises(UserError):
            wiz.create_requests()

    def test_05_create_requests_non_auto_approved(self):
        wiz = self._create_correct_multi_id_request_wizard()
        wiz.create_requests()
        targets = self._target_model.search([("registrant_id", "in", self.all_individual.ids)])
        for individual in self.all_individual:
            target = targets.filtered(lambda rec: rec.registrant_id.id == individual.id)  # noqa: B023
            self.assertNotEqual(target.ids, [], "Should have some ID queue created!")
            self.assertEqual(target.status, "new", "Status should be `new`!")
            self.assertEqual(
                target.id_type.ids,
                self.env.ref("spp_idpass.id_type_idpass").ids,
                "Id type should be the wizard ID type!",
            )
            self.assertEqual(target.date_requested, date.today())
            self.assertEqual(
                target.requested_by,
                self.env.user,
                "The requestor should be current user!",
            )

    def test_06_create_requests_auto_approved(self):
        wiz = self._create_correct_multi_id_request_wizard()
        self.env["ir.config_parameter"].set_param("spp_id_queue.auto_approve_id_request", True)
        wiz.create_requests()
        targets = self._target_model.search([("registrant_id", "in", self.all_individual.ids)])
        for individual in self.all_individual:
            target = targets.filtered(lambda rec: rec.registrant_id.id == individual.id)  # noqa: B023
            self.assertEqual(target.status, "approved", "Status should be `approved`!")
