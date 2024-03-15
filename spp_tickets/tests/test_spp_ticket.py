from odoo.tests.common import TransactionCase


class TestSPPTicket(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Ticket = self.env["spp.ticket"]
        self.partner_demo = self.env.ref("base.res_partner_2")
        self.tag_demo = self.env["spp.ticket.tag"].create({"name": "Test Tag"})

    def test_create_ticket(self):
        """Test creating a ticket."""
        ticket = self.Ticket.create(
            {
                "name": "Test Ticket",
                "description": "This is a test ticket.",
                "ticket_type": "inquiry",
                "priority": "low",
                "partner_id": self.partner_demo.id,
                "tag_ids": [(6, 0, [self.tag_demo.id])],
            }
        )
        self.assertTrue(ticket, "The ticket was not created.")

    def test_ticket_status_update(self):
        """Test updating a ticket's status."""
        ticket = self.Ticket.create(
            {
                "name": "Status Update Test",
                "description": "Test for updating status.",
                "ticket_type": "request",
                "priority": "medium",
                "partner_id": self.partner_demo.id,
            }
        )
        ticket.status = "in_progress"
        self.assertEqual(ticket.status, "in_progress", "The ticket status was not updated.")
