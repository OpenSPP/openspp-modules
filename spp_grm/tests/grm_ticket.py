from odoo.tests.common import TransactionCase


class SPPGRMTicketTests(TransactionCase):
    def setUp(self):
        super().setUp()
        self.ticket = self.env["spp.grm.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test Description",
                "partner_id": self.env.ref("base.res_partner_1").id,
            }
        )

    def ticket_creation(self):
        new_ticket = self.env["spp.grm.ticket"].create(
            {
                "name": "New Ticket",
                "description": "New Description",
                "partner_id": self.env.ref("base.res_partner_2").id,
            }
        )
        self.assertEqual(new_ticket.name, "New Ticket")

    def ticket_number_generation(self):
        self.assertNotEqual(self.ticket.number, "/")

    def ticket_assignment(self):
        self.ticket.write({"user_id": self.env.ref("base.user_admin").id})
        self.assertEqual(self.ticket.user_id, self.env.ref("base.user_admin"))

    def ticket_stage_transition(self):
        stage_closed = self.env["spp.grm.ticket.stage"].search([("closed", "=", True)], limit=1)
        self.ticket.write({"stage_id": stage_closed.id})
        self.assertEqual(self.ticket.stage_id, stage_closed)

    def ticket_copy(self):
        copied_ticket = self.ticket.copy()
        self.assertNotEqual(copied_ticket.number, self.ticket.number)

    def ticket_assign_to_me(self):
        self.ticket.assign_to_me()
        self.assertEqual(self.ticket.user_id, self.env.user)
