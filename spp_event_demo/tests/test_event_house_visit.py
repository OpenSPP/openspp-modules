import logging

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class EventHouseVisitTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(EventHouseVisitTest, cls).setUpClass()

        # Initial Setup of Variables
        cls.group_1 = cls.env["res.partner"].create(
            {
                "name": "Group 1",
                "is_registrant": True,
                "is_group": True,
            }
        )
        cls.house_visit_1 = cls.env["spp.event.house.visit"].create(
            {
                "registrant": cls.group_1.id,
                "summary": "Testing Visit",
                "description": "This visit is for testing only",
            }
        )

    def test_01_check_active_house_visit(self):
        self.group_1._compute_active_house_visit()
        event_id = self.env["spp.event.data"].search(
            [
                ("model", "=", "spp.event.house.visit"),
                ("res_id", "=", self.house_visit_1.id),
            ]
        )
        self.assertEqual(
            self.group_1.active_house_visit.id,
            event_id.id,
        )

    def test_02_check_name(self):
        self.assertEqual(
            self.group_1.active_house_visit.name,
            "House Visit - [Testing Visit]",
        )

    def test_03_recheck_active_house_visit_after_entering_new_visit(self):
        if self.group_1.active_house_visit:
            self.group_1.end_active_event(self.group_1.active_house_visit)

        vals = {
            "registrant": self.group_1.id,
            "summary": "Testing Visit 2",
            "description": "This visit is for testing again",
        }
        house_visit_2 = self.env["spp.event.house.visit"].create(vals)

        self.group_1._compute_active_house_visit()
        event_id = self.env["spp.event.data"].search(
            [("model", "=", "spp.event.house.visit"), ("res_id", "=", house_visit_2.id)]
        )
        self.assertEqual(
            self.group_1.active_house_visit.id,
            event_id.id,
        )
