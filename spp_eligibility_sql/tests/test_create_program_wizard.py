from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestCreateProgramWiz(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_1 = cls.env["res.partner"].create(
            {
                "name": "Group 1",
                "is_group": True,
            }
        )
        cls._program_create_wiz = cls.env["g2p.program.create.wizard"].create(
            {
                "name": "Test Program 1 [SQL Elibigility]",
                "eligibility_kind": "sql_eligibility",
                "sql_query": "select id from res_partner where family_name = 'Butay'",
                "rrule_type": "monthly",
                "cycle_duration": 1,
                "currency_id": cls.env.company.currency_id.id,
                "entitlement_kind": "default",
                "amount_per_cycle": 1.0,
                "amount_per_individual_in_group": 1.0,
            }
        )
        cls.journal_id = cls._program_create_wiz.create_journal(
            cls._program_create_wiz.name, cls._program_create_wiz.currency_id.id
        )

    def test_01_check_sql_query_onchange(self):
        self._program_create_wiz._sql_query_onchange()
        self.assertEqual(
            self._program_create_wiz.sql_query_valid,
            "recheck",
            "Correct SQL Query validation state",
        )

    def test_02_test_sql_query(self):
        self._program_create_wiz.test_sql_query()

        self.assertEqual(self._program_create_wiz.sql_query_valid, "valid")
        self.assertEqual(
            self._program_create_wiz.sql_query_valid_message, "The SQL Query is valid but it did not return any record."
        )
        self.assertEqual(self._program_create_wiz.sql_record_count, 0)
        self.assertEqual(self._program_create_wiz.state, "step1")

        self._program_create_wiz.sql_query = "select id from res_partner"
        self._program_create_wiz.test_sql_query()

        self.assertEqual(self._program_create_wiz.sql_query_valid, "valid")
        self.assertFalse(self._program_create_wiz.sql_query_valid_message)
        self.assertEqual(self._program_create_wiz.sql_record_count, 1)
        self.assertEqual(self._program_create_wiz.state, "step1")

        self._program_create_wiz.target_type = "individual"
        self._program_create_wiz.test_sql_query()

        self.assertEqual(self._program_create_wiz.sql_query_valid, "valid")
        self.assertEqual(
            self._program_create_wiz.sql_query_valid_message, "The SQL Query is valid but it did not return any record."
        )
        self.assertEqual(self._program_create_wiz.sql_record_count, 0)
        self.assertEqual(self._program_create_wiz.state, "step1")

    def test_03_check_required_fields(self):
        with self.assertRaisesRegex(UserError, "The SQL Query must return 1 or more record."):
            self._program_create_wiz._check_required_fields()

        with self.assertRaisesRegex(UserError, "The SQL Query must be validated first."):
            self._program_create_wiz.sql_query_valid = False
            self._program_create_wiz._check_required_fields()

        with self.assertRaisesRegex(UserError, "A SQL Query is needed for this eligibility criteria type."):
            self._program_create_wiz.sql_query = False
            self._program_create_wiz._check_required_fields()

    def test_04_get_eligibility_manager(self):
        self._program_create_wiz.sql_query = "select id from res_partner"
        self._program_create_wiz.sql_record_count = 1
        self.program = self._program_create_wiz.create_program()
        eligibility_manager = self._program_create_wiz._get_eligibility_manager(self.program["res_id"])

        self.assertIn("eligibility_managers", eligibility_manager)
        self.assertIn(4, eligibility_manager["eligibility_managers"][0])
