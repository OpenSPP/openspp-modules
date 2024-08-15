from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestProgram(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Group", "is_registrant": True, "is_group": True})

    def test_create_program_sql_eligibility(self):
        name = "Test Program 1"
        sql_query = "select id from res_partner"
        entitlement_kind = "default"
        entitlement_vars = {
            "amount_per_cycle": 1.0,
            "amount_per_individual_in_group": 1.0,
            "sql_record_count": 1,
        }
        current_count = self.env["g2p.program"].search_count([])

        self.env["g2p.program"].create_program_sql_eligibility(name, sql_query, entitlement_kind, entitlement_vars)

        self.assertEqual(current_count + 1, self.env["g2p.program"].search_count([]))

        with self.assertRaisesRegex(UserError, "The entitlement kind must be specified."):
            self.env["g2p.program"].create_program_sql_eligibility(name, sql_query, None, entitlement_vars)

        with self.assertRaisesRegex(
            UserError, "The program name, SQL query, and entitlement dictionary must be provided."
        ):
            self.env["g2p.program"].create_program_sql_eligibility(name, None, entitlement_kind, entitlement_vars)
