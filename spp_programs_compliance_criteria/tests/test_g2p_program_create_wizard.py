from unittest.mock import patch

from odoo.exceptions import ValidationError
from odoo.tools import mute_logger

from . import common


class TestG2pProgramCreateWiz(common.Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._test = cls.program_create_wizard({})

    def test_01_create_program_without_compliance_manager(self):
        self._test._check_compliance_manager_info()
        action = self._test.create_program()
        program = self.env["g2p.program"].browse(action["res_id"])
        self.assertFalse(
            bool(program.compliance_managers),
            "Should not create compliance manager for new program!",
        )

    def test_02_create_program_errors(self):
        self._test.compliance_criteria = True
        self._test.compliance_kind = None
        error = "^Not enough information for creating compliance manager!$"
        with self.assertRaisesRegex(ValidationError, error):
            self._test.create_program()
        self._test.compliance_kind = "g2p.program_membership.manager.default"
        self._test.compliance_domain = None
        with self.assertRaisesRegex(ValidationError, error):
            self._test.create_program()
        self._test.compliance_kind = "g2p.program_membership.manager.sql"
        with self.assertRaisesRegex(ValidationError, error):
            self._test.create_program()
        self._test.compliance_kind = "g2p.program_membership.manager.tags"
        with self.assertRaisesRegex(ValidationError, error):
            self._test.create_program()

    def test_03_create_program_default_compliance_manager(self):
        self._test.write(
            {
                "compliance_criteria": True,
                "compliance_kind": "g2p.program_membership.manager.default",
                "compliance_domain": "[['id', '>', 2]]",
            }
        )
        action = self._test.create_program()
        program = self.env["g2p.program"].browse(action["res_id"])
        self.assertTrue(
            bool(program.compliance_managers),
            "Should create compliance manager for new program!",
        )
        manager = program.compliance_managers[0].manager_ref_id
        self.assertEqual(
            manager._name,
            "g2p.program_membership.manager.default",
            "Manager should be correct!",
        )
        self.assertEqual(manager.eligibility_domain, "[['id', '>', 2]]", "Manager should be correct!")
        self.assertEqual(manager.program_id, program, "Manager should be correct!")

    def test_04_create_program_sql_compliance_manager(self):
        self._test.write(
            {
                "compliance_criteria": True,
                "compliance_kind": "g2p.program_membership.manager.sql",
                "compliance_sql": "SELECT id FROM res_partner",
                "compliance_sql_query_valid": "valid",
            }
        )
        action = self._test.create_program()
        program = self.env["g2p.program"].browse(action["res_id"])
        self.assertTrue(
            bool(program.compliance_managers),
            "Should create compliance manager for new program!",
        )
        manager = program.compliance_managers[0].manager_ref_id
        self.assertEqual(
            manager._name,
            "g2p.program_membership.manager.sql",
            "Manager should be correct!",
        )
        self.assertEqual(
            manager.sql_query,
            "SELECT id FROM res_partner",
            "Manager should be correct!",
        )
        self.assertEqual(manager.program_id, program, "Manager should be correct!")

    def test_05_create_program_tag_compliance_manager(self):
        self._test.write(
            {
                "compliance_criteria": True,
                "compliance_kind": "g2p.program_membership.manager.tags",
                "compliance_tag_id": self._tag.id,
            }
        )
        action = self._test.create_program()
        program = self.env["g2p.program"].browse(action["res_id"])
        self.assertTrue(
            bool(program.compliance_managers),
            "Should create compliance manager for new program!",
        )
        manager = program.compliance_managers[0].manager_ref_id
        self.assertEqual(
            manager._name,
            "g2p.program_membership.manager.tags",
            "Manager should be correct!",
        )
        self.assertEqual(manager.tags_id, self._tag, "Manager should be correct!")
        self.assertEqual(manager.program_id, program, "Manager should be correct!")

    def test_06_onchange_compliance_sql(self):
        self._test.compliance_sql_query_valid = "valid"
        self._test._onchange_compliance_sql()
        self.assertNotEqual(
            self._test.compliance_sql_query_valid,
            "valid",
            "Compliance SQL should not be valid after change!",
        )

    @mute_logger("odoo.addons.spp_eligibility_sql.wizard.create_program_wizard")
    def test_07_test_compliance_sql_query_invalid(self):
        self._test.compliance_sql = "SELECT id FROM res_partner"
        with self.assertLogs(
            "odoo.addons.spp_programs_compliance_criteria.wizards.g2p_program_create_wizard",
            level="ERROR",
        ) as log_catcher:
            self._test.test_compliance_sql_query()
            self.assertEqual(
                self._test.compliance_sql_query_valid,
                "invalid",
                "Compliance SQL should not be valid after change!",
            )
            for output in log_catcher.output:
                self.assertRegex(output, "^.*Query is not valid!.*$", "All record is now on cached!")

    @mute_logger("odoo.addons.spp_eligibility_sql.wizard.create_program_wizard")
    @patch("odoo.sql_db.Cursor.dictfetchall")
    def test_07_test_compliance_sql_query_valid(self, mocker):
        mocker.__name__ = "Mock Cursor"
        mocker.return_value = [{"id": 1}]
        self._test.compliance_sql = "SELECT id FROM res_partner"
        self._test.test_compliance_sql_query()
        self.assertEqual(
            self._test.compliance_sql_query_valid,
            "valid",
            "Record is now mocked return!",
        )
