from odoo.exceptions import UserError

from .common import Common


class TestBatchCreateWiz(Common):
    def setUp(self):
        super().setUp()
        self._test_g2p_id_type = self.env["g2p.id.type"].create(
            {
                "name": "G2P ID Type",
                "target_type": "both",
            }
        )
        self._test_spp_id_pass = self.env["spp.id.pass"].create(
            {
                "name": "SPP ID Pass",
                "id_type": self._test_g2p_id_type.id,
            }
        )
        self._test_queue_1 = self._create_test_queue(self._test_individual_1.id)
        self._test_queue_2 = self._create_test_queue(
            self._test_individual_2.id, status="new"
        )
        self._test_queue_3 = self._create_test_queue(
            self._test_individual_3.id,
            id_type=self._test_g2p_id_type.id,
            idpass_id=self._test_spp_id_pass.id,
        )
        self._model = self.env["spp.batch.create.wizard"]

    def test_01_default_queue_ids_and_state(self):
        with self.assertRaisesRegex(UserError, "^.*no selected id requests.*$"):
            self._model.create({"id_type": self._test_g2p_id_type.id})
        with self.assertRaisesRegex(UserError, "^No approved id requests selected.$"):
            self._model.with_context(active_ids=[self._test_queue_2.id]).create(
                {"id_type": self.env.ref("spp_idpass.id_template_idpass").id}
            )
        test_batch_1 = self._model.with_context(
            active_ids=[self._test_queue_1.id]
        ).create({"id_type": self.env.ref("spp_idpass.id_template_idpass").id})
        self.assertEqual(
            test_batch_1.state, "step2", "Batch Create Wiz state should be `step2`!"
        )
        self.assertEqual(
            test_batch_1.id_count, 1, "Batch Create Wiz id count should be 1!"
        )
        self.assertListEqual(
            test_batch_1.queue_ids.ids,
            self._test_queue_1.ids,
            "List of queue in context must be equal with childs!",
        )
        test_batch_2 = self._model.with_context(
            active_ids=[self._test_queue_1.id, self._test_queue_3.id]
        ).create({"id_type": self.env.ref("spp_idpass.id_template_idpass").id})
        self.assertEqual(
            test_batch_2.state, "step1", "Batch Create Wiz state should be `step1`!"
        )

    def test_02_compute_batches_count(self):
        self._test_queue_2.status = "approved"
        test_batch = self._model.with_context(
            active_ids=[self._test_queue_1.id, self._test_queue_2.id]
        ).create({"id_type": self.env.ref("spp_idpass.id_template_idpass").id})
        self.assertEqual(test_batch.batches_count, 1, "Batch count should be 1!")
        test_batch.write({"max_id_per_batch": 1})
        self.assertEqual(test_batch.batches_count, 2, "Batch count should be 2!")

    def test_03_next_step(self):
        test_batch = self._model.with_context(
            active_ids=[self._test_queue_1.id, self._test_queue_3.id]
        ).create({"id_type": self.env.ref("spp_idpass.id_template_idpass").id})
        test_batch.write(
            {"idpass_id": self.env.ref("spp_idpass.id_template_idpass").id}
        )
        test_batch.next_step()
        self.assertEqual(
            test_batch.state, "step2", "Batch Create Wiz now should be in `step2`!"
        )
        self.assertEqual(test_batch.id_count, 1, "Test queue 3 should be removed!")
        self.assertListEqual(
            test_batch.queue_ids.ids,
            [self._test_queue_1.id],
            "Test queue 3 should be removed!",
        )

    def test_04_create_batch(self):
        self._test_queue_2.status = "approved"
        test_batch = self._model.with_context(
            active_ids=[self._test_queue_1.id, self._test_queue_2.id]
        ).create(
            {
                "name": "Create Test Batch 01",
                "id_type": self.env.ref("spp_idpass.id_template_idpass").id,
                "max_id_per_batch": 1,
            }
        )
        test_batch.create_batch()
        new_batches_created = self.env["spp.print.queue.batch"].search(
            [("name", "like", "Create Test Batch 01")]
        )
        self.assertEqual(
            len(new_batches_created), 2, "Batch create wiz should create 2 new batches!"
        )
        self.assertNotEqual(
            self._test_queue_1.batch_id.id,
            False,
            "Queue 1 should be in some batch now!",
        )
        self.assertNotEqual(
            self._test_queue_2.batch_id.id,
            False,
            "Queue 2 should be in some batch now!",
        )
        self.assertNotEqual(
            self._test_queue_1.batch_id,
            self._test_queue_2.batch_id,
            "Queue 1 & Queue 2 should not be in same batch!",
        )
