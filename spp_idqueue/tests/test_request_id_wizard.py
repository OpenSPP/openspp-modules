from datetime import date

from odoo.exceptions import UserError

from .common import Common


class TestRequestIdWiz(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._model = cls.env["spp.print.queue.wizard"]

    def _create_correct_queue_wizard(self):
        wiz = self._model.create(
            {
                "registrant_id": self._test_group.id,
                "id_type": self.env.ref("spp_idpass.id_type_idpass").id,
            }
        )
        wiz._onchange_template()
        return wiz

    def test_01_compute_target_type(self):
        individual_target = self._model.create({"registrant_id": self._test_individual_1.id})
        self.assertEqual(
            individual_target.target_type,
            "individual",
            "This wizard should target individual!",
        )
        group_target = self._model.create({"registrant_id": self._test_group.id})
        self.assertEqual(group_target.target_type, "group", "This wizard should target group!")

    def test_02_onchange_template(self):
        wiz = self._create_correct_queue_wizard()
        self.assertTrue(wiz.is_idpass, "Id Type should be ID Pass!")

    def test_03_request_id_non_id_type(self):
        wiz = self._model.create({"registrant_id": self._test_group.id})
        with self.assertRaises(UserError):
            wiz.request_id()

    def test_04_request_id_not_auto_approve(self):
        wiz = self._create_correct_queue_wizard()
        wiz.request_id()
        id_queue = self.env["spp.print.queue.id"].search([("registrant_id", "=", self._test_group.id)], limit=1)
        self.assertNotEqual(id_queue.ids, [], "Should have some ID queue created!")
        self.assertEqual(id_queue.status, "new", "Status should be `new`!")
        self.assertEqual(
            id_queue.id_type.ids,
            self.env.ref("spp_idpass.id_type_idpass").ids,
            "Id type should be the wizard ID type!",
        )
        self.assertEqual(id_queue.date_requested, date.today())
        self.assertEqual(
            id_queue.requested_by,
            self.env.user,
            "The requestor should be current user!",
        )

    def test_05_request_id_auto_approve(self):
        wiz = self._create_correct_queue_wizard()
        self.env["ir.config_parameter"].set_param("spp_id_queue.auto_approve_id_request", True)
        wiz.request_id()
        id_queue = self.env["spp.print.queue.id"].search([("registrant_id", "=", self._test_group.id)], limit=1)
        self.assertEqual(id_queue.status, "approved", "Status should be `approved`!")
