from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestSQLBasedEligibilityManager(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner", "is_group": False})
        cls.program_id = cls.env["g2p.program"].create(
            {
                "name": "Test Program",
                "target_type": "individual",
            }
        )
        cls.membership = cls.env["g2p.program_membership"].create(
            {
                "partner_id": cls.partner.id,
                "program_id": cls.program_id.id,
                "state": "enrolled",
            }
        )
        cls.sql_manager = cls.env["g2p.program_membership.manager.sql"].create(
            {
                "name": "SQL Manager",
                "program_id": cls.program_id.id,
            }
        )

    def test_sql_query_onchange(self):
        self.sql_manager._sql_query_onchange()

        self.assertEqual(
            self.sql_manager.sql_query_valid,
            "recheck",
        )
        self.assertFalse(self.sql_manager.sql_query_valid_message)
        self.assertEqual(self.sql_manager.sql_record_count, 0)

    def test_prepare_eligible_domain(self):
        domain = self.sql_manager._prepare_eligible_domain(membership=self.program_id.program_membership_ids)

        self.assertEqual(domain, [("id", "in", [self.partner.id]), ("disabled", "=", False), ("is_group", "=", False)])

        self.program_id.target_type = "group"
        domain = self.sql_manager._prepare_eligible_domain(beneficiaries=self.partner.ids)
        self.assertEqual(domain, [("id", "in", [self.partner.id]), ("disabled", "=", False), ("is_group", "=", True)])

    def test_generate_sql_query(self):
        self.sql_manager.sql_query = "select id from res_partner where name = 'Test Partner'"
        sql_query = self.sql_manager._generate_sql_query()

        self.assertIn(self.sql_manager.sql_query, sql_query)
        self.assertIn("active AND disabled IS NULL AND NOT is_group", sql_query)

        self.program_id.target_type = "group"
        self.sql_manager.sql_query = "insert into res_partner (name) values ('Test Partner')"
        sql_query = self.sql_manager._generate_sql_query()

        self.assertIn("DML ERROR", sql_query)
        self.assertIn("active AND disabled IS NULL AND is_group", sql_query)

    def test_get_beneficiaries_sql_query(self):
        with self.assertRaisesRegex(
            UserError, "The SQL Query is not valid. Be sure to validate this in the Eligibility Manager."
        ):
            self.sql_manager._get_beneficiaries_sql_query()

        self.sql_manager.sql_query = "select id from res_partner"
        self.sql_manager.sql_query_valid = "valid"

        sql_query_result = self.sql_manager._get_beneficiaries_sql_query()

        self.assertIn(self.partner.id, sql_query_result)

    def test_sql_query(self):
        self.sql_manager.sql_query = "select id from res_partner"
        self.sql_manager.test_sql_query()

        self.assertEqual(self.sql_manager.sql_query_valid, "valid")
        self.assertFalse(self.sql_manager.sql_query_valid_message)
        self.assertEqual(self.sql_manager.sql_record_count, 1)

        self.sql_manager.sql_query = "select id from res_partner where name = 'Wrong Name'"
        self.sql_manager.test_sql_query()

        self.assertEqual(self.sql_manager.sql_query_valid, "valid")
        self.assertEqual(
            self.sql_manager.sql_query_valid_message, "The SQL Query is valid but it did not return any record."
        )
        self.assertEqual(self.sql_manager.sql_record_count, 0)

    def test_enroll_eligible_registrants(self):
        res = self.sql_manager.enroll_eligible_registrants(self.program_id.program_membership_ids)

        self.assertTrue(res)
        self.assertEqual(res.partner_id, self.partner)
        self.assertEqual(res.program_id, self.program_id)

    def test_verify_eligibility(self):
        beneficiaries = self.sql_manager._verify_eligibility(self.program_id.program_membership_ids)

        self.assertIn(self.partner.id, beneficiaries)

    def test_import_eligible_registrants(self):
        self.env["res.partner"].create({"name": "New Test Partner", "is_group": False})

        self.sql_manager.sql_query = "select id from res_partner"
        self.sql_manager.sql_query_valid = "valid"
        ben_count = self.sql_manager.import_eligible_registrants()

        self.assertEqual(ben_count, 1)

    def test_import_registrants_async(self):
        new_partner = self.env["res.partner"].create({"name": "New Test Partner", "is_group": False})
        current_count = len(self.env["queue.job"].search([]))

        self.sql_manager._import_registrants_async(new_partner.ids)

        # 2 jobs are created for the import and the verification
        # - the actual job
        # - the function after running the actual job
        self.assertEqual(current_count + 2, len(self.env["queue.job"].search([])))

    def test_mark_import_as_done(self):
        self.sql_manager.mark_import_as_done()

        self.assertFalse(self.program_id.locked)
        self.assertFalse(self.program_id.locked_reason)

    def test_import_registrants(self):
        self.sql_manager.sql_query = "select id from res_partner"
        self.sql_manager.sql_query_valid = "valid"
        new_partner = self.env["res.partner"].create({"name": "New Test Partner", "is_group": False})

        self.sql_manager._import_registrants(new_partner.ids, do_count=True)

        self.assertEqual(len(self.program_id.program_membership_ids), 2)
        self.assertIn(self.partner.id, self.program_id.program_membership_ids.mapped("partner_id").ids)
        self.assertIn(self.program_id.id, self.program_id.program_membership_ids.mapped("program_id").ids)
