from odoo.tests import TransactionCase


class TestCreateProgramWiz(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._program_create_wiz = cls.env["g2p.program.create.wizard"].create(
            {
                "name": "Test Program 1 [SQL Elibigility]",
                "eligibility_kind": "sql_eligibility",
                "sql_query": "select id from res_partner where family_name = 'Butay'",
                "rrule_type": "monthly",
                "cycle_duration": 1,
                "currency_id": cls.env.company.currency_id.id,
                "entitlement_kind": "default",
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
