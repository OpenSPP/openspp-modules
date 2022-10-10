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
                "summary": "Testing Visit",
                "description": "This visit is for testing only",
            }
        )
        cls.event_data_1 = cls.env["spp.event.data"].create(
            {
                "partner_id": cls.group_1.id,
                "model": "spp.event.house.visit",
                "res_id": cls.house_visit_1.id,
            }
        )

    def test_01_check_active_house_visit(self):
        self.group_1._compute_active_house_visit()
        self.assertEqual(
            self.group_1.active_house_visit.id,
            self.event_data_1.id,
        )

    def test_02_check_name(self):
        self.assertEqual(
            self.group_1.active_house_visit.name,
            "House Visit - [Testing Visit]",
        )

    def test_03_recheck_active_house_visit_after_entering_new_visit(self):
        vals_house = {
            "summary": "Testing Visit 2",
            "description": "This visit is for testing again",
        }
        house_visit_2 = self.env["spp.event.house.visit"].create(vals_house)
        vals_event_data = {
            "partner_id": self.group_1.id,
            "model": "spp.event.house.visit",
            "res_id": house_visit_2.id,
        }
        event_data_2 = self.env["spp.event.data"].create(vals_event_data)

        self.group_1._compute_active_house_visit()
        self.assertEqual(
            self.group_1.active_house_visit.id,
            event_data_2.id,
        )
