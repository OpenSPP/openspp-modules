from odoo.tests import TransactionCase


class TestCreateProgramWiz(TransactionCase):
    def setUp(self):
        super().setUp()
        self._program_create_wiz = self.env["g2p.program.create.wizard"].create(
            {
                "name": "Test Program 1 [SQL Elibigility]",
                "eligibility_kind": "sql_eligibility",
                "sql_query": "select id from res_partner where z_ind_grp_num_eligible_children_under_12_months > 0",
                "rrule_type": "monthly",
                "cycle_duration": 1,
                "currency_id": self.env.company.currency_id.id,
                "entitlement_kind": "cash",
                "max_amount": 5.0,
            }
        )
        self.journal_id = self._program_create_wiz.create_journal(
            self._program_create_wiz.name, self._program_create_wiz.currency_id.id
        )

        # self.program = self.env["g2p.program"].create(
        #    {
        #        "name": self._program_create_wiz.name,
        #        "journal_id": self.journal_id,
        #        "target_type": self._program_create_wiz.target_type,
        #    }
        # )

    def _update_program_create_wiz(self):
        self._program_create_wiz.write(
            {
                "entitlement_cash_item_ids": [
                    (
                        0,
                        0,
                        {
                            "amount": 5.0,
                        },
                    ),
                ],
            }
        )

    def test_01_check_sql_query_onchange(self):
        self._update_program_create_wiz()
        self._program_create_wiz._sql_query_onchange()
        self.assertEqual(
            self._program_create_wiz.sql_query_valid,
            "recheck",
            "Correct SQL Query validation state",
        )
