from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestSppServicePoint(TransactionCase):
    def setUp(self):
        super().setUp()
        self.test_service_point_1 = self.env["spp.service.point"].create(
            {
                "name": "service point 1",
            }
        )
        self.test_service_point_2 = self.env["spp.service.point"].create(
            {
                "name": "service point 2",
            }
        )
        self.test_service_point_3 = self.env["spp.service.point"].create(
            {
                "name": "service point 3",
            }
        )
        self.test_service_point_4 = self.env["spp.service.point"].create(
            {
                "name": "service point 4",
            }
        )
        self.test_group = self.env["res.partner"].create(
            {
                "name": "group 1",
                "is_registrant": True,
                "is_group": True,
            }
        )
        self.test_program_1 = self.env["g2p.program"].create(
            {
                "name": "program 1",
            }
        )
        self.test_program_2 = self.env["g2p.program"].create(
            {
                "name": "program 2",
            }
        )
        self.test_cycle_1 = self.env["g2p.cycle"].create(
            {
                "name": "cycle 1",
                "program_id": self.test_program_1.id,
                "start_date": fields.Date.today(),
                "end_date": fields.Date.add(fields.Date.today(), days=30),
            }
        )
        self.test_cycle_2 = self.env["g2p.cycle"].create(
            {
                "name": "cycle 2",
                "program_id": self.test_program_2.id,
                "start_date": fields.Date.today(),
                "end_date": fields.Date.add(fields.Date.today(), days=30),
            }
        )
        self.env["g2p.entitlement"].create(
            [
                {
                    "cycle_id": self.test_cycle_1.id,
                    "partner_id": self.test_group.id,
                    "initial_amount": 50_000,
                    "service_point_ids": [
                        (
                            6,
                            0,
                            [
                                self.test_service_point_1.id,
                                self.test_service_point_2.id,
                            ],
                        )
                    ],
                },
                {
                    "cycle_id": self.test_cycle_2.id,
                    "partner_id": self.test_group.id,
                    "initial_amount": 50_000,
                    "service_point_ids": [
                        (
                            6,
                            0,
                            [
                                self.test_service_point_1.id,
                                self.test_service_point_3.id,
                            ],
                        )
                    ],
                },
            ]
        )

    def test_01_compute_program_id(self):
        service_point = (
            self.test_service_point_1
            | self.test_service_point_2
            | self.test_service_point_3
            | self.test_service_point_4
        )
        service_point._compute_program_id()
        self.assertIn(
            self.test_program_1,
            self.test_service_point_1.program_id,
            "Program 1 should be linked to service point 1!",
        )
        self.assertIn(
            self.test_program_1,
            self.test_service_point_2.program_id,
            "Program 1 should be linked to service point 2!",
        )
        self.assertIn(
            self.test_program_2,
            self.test_service_point_1.program_id,
            "Program 2 should be linked to service point 1!",
        )
        self.assertIn(
            self.test_program_2,
            self.test_service_point_3.program_id,
            "Program 2 should be linked to service point 3!",
        )
        self.assertNotIn(
            self.test_program_1,
            self.test_service_point_3.program_id,
            "Program 1 should not be linked to service point 3!",
        )
        self.assertNotIn(
            self.test_program_2,
            self.test_service_point_2.program_id,
            "Program 2 should not be linked to service point 2!",
        )
        self.assertFalse(
            bool(self.test_service_point_4.program_id.ids),
            "Service point 4 should not be linked to any program!",
        )

    def test_02_search_program_id(self):
        with self.assertRaisesRegex(ValidationError, "Operator is not supported!"):
            self.env["spp.service.point"].search([("program_id", "in", [1, 2])])
        res = self.env["spp.service.point"].search([("program_id", "=", self.test_program_1.id)])
        self.assertIn(
            self.test_service_point_1,
            res,
            "Service point 1 should be in search result when searching for program_id = program_1.id!",
        )
        self.assertIn(
            self.test_service_point_2,
            res,
            "Service point 2 should be in search result when searching for program_id = program_1.id!",
        )
        self.assertNotIn(
            self.test_service_point_3,
            res,
            "Service point 3 should not be in search result when searching for program_id = program_1.id!",
        )
        self.assertNotIn(
            self.test_service_point_4,
            res,
            "Service point 4 should not be in search result when searching for program_id = program_1.id!",
        )
        res = self.env["spp.service.point"].search([("program_id", "=", self.test_program_2.id)])
        self.assertIn(
            self.test_service_point_1,
            res,
            "Service point 1 should be in search result when searching for program_id = program_2.id!",
        )
        self.assertIn(
            self.test_service_point_3,
            res,
            "Service point 3 should be in search result when searching for program_id = program_2.id!",
        )
        self.assertNotIn(
            self.test_service_point_2,
            res,
            "Service point 2 should not be in search result when searching for program_id = program_2.id!",
        )
        self.assertNotIn(
            self.test_service_point_4,
            res,
            "Service point 4 should not be in search result when searching for program_id = program_1.id!",
        )
