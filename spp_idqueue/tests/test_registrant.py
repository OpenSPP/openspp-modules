from .common import Common


class TestRegistrant(Common):
    def test_01_open_request_id_wizard(self):
        print_queue_wiz = self.env["spp.print.queue.wizard"]
        test_group_print_queue_ids = print_queue_wiz.search([("registrant_id", "=", self._test_group.id)])
        self.assertEqual(
            test_group_print_queue_ids,
            print_queue_wiz.browse([]),
            "Test group should not have any print queue wizard yet!",
        )
        self._test_group.open_request_id_wizard()
        test_group_print_queue_ids = print_queue_wiz.search([("registrant_id", "=", self._test_group.id)])
        self.assertNotEqual(
            test_group_print_queue_ids,
            print_queue_wiz.browse([]),
            "Test group should now having print queue wizard!",
        )
