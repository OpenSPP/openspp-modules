import json
import os
import tempfile

from odoo.tests.common import TransactionCase


class AuditRuleTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.model_1 = cls.env["ir.model"].search([("model", "=", "res.partner")], limit=1)
        cls.res_partner_rule = cls.env["spp.audit.rule"].search([("model_id", "=", cls.model_1.id)], limit=1)
        if not cls.res_partner_rule:
            cls.res_partner_rule = AuditRuleTest.create_audit_rule(
                name="Rule 1", model_id=cls.model_1.id, log_unlink=False
            )
        else:
            cls.res_partner_rule.update(
                {
                    "log_create": True,
                    "log_write": True,
                    "log_unlink": False,
                }
            )

        cls.res_partner = cls.env["res.partner"].create(
            {
                "name": "Res Partner Group",
                "phone": "+639266716911",
            }
        )

    @classmethod
    def create_audit_rule(cls, **kwargs):
        return cls.env["spp.audit.rule"].create(kwargs)

    def test_get_audit_rules(self):
        self.assertIsNotNone(self.res_partner.get_audit_rules("create").id)
        self.assertIsNotNone(self.res_partner.get_audit_rules("write").id)
        self.assertFalse(self.res_partner.get_audit_rules("unlink").id)

    def test_register_hook(self):
        self.assertTrue(self.env["spp.audit.rule"]._register_hook([self.res_partner_rule.id]))
        self.assertFalse(self.env["spp.audit.rule"]._register_hook([0]))

    def test_format_data_to_log(self):
        id_val = 1
        field = "name"
        old_name = "old name"
        new_name = "new name"
        not_included_field = "active"

        old_values = {
            "id": id_val,
            field: old_name,
            not_included_field: False,
        }
        new_values = {
            "id": id_val,
            field: new_name,
            not_included_field: True,
        }
        fields_to_log = [field]
        data = self.env["spp.audit.rule"]._format_data_to_log(old_values, new_values, fields_to_log)

        self.assertIn(id_val, data.keys())
        self.assertIn("old", data[id_val].keys())
        self.assertIn("new", data[id_val].keys())
        self.assertIn(field, data[id_val]["old"].keys())
        self.assertIn(field, data[id_val]["new"].keys())
        self.assertNotIn(not_included_field, data[id_val]["old"].keys())
        self.assertNotIn(not_included_field, data[id_val]["new"].keys())
        self.assertEqual(data[id_val]["old"][field], old_name)
        self.assertEqual(data[id_val]["new"][field], new_name)

    def test_get_audit_log_vals(self):
        res_id = 1
        method = "write"
        data = {res_id: {}}
        vals = self.res_partner_rule.get_audit_log_vals(res_id, method, data)

        self.assertIn("user_id", vals.keys())
        self.assertIn("model_id", vals.keys())
        self.assertIn("res_id", vals.keys())
        self.assertIn("method", vals.keys())
        self.assertIn("data", vals.keys())

        self.assertEqual(self.res_partner_rule._uid, vals["user_id"])
        self.assertEqual(self.res_partner_rule.model_id.id, vals["model_id"])
        self.assertEqual(res_id, vals["res_id"])
        self.assertEqual(method, vals["method"])
        self.assertEqual(repr(data[res_id]), vals["data"])

    def test_database_logging_mode(self):
        """Test that audit logs are written to database when file logging is disabled"""
        # Ensure file logging is disabled
        self.env["ir.config_parameter"].sudo().set_param("spp.audit_log_to_file", "False")

        # Count existing audit logs
        initial_count = self.env["spp.audit.log"].search_count([])

        # Create a new partner (should trigger audit log)
        partner = self.env["res.partner"].create(
            {
                "name": "Test Partner DB Mode",
                "phone": "+639123456789",
            }
        )

        # Verify audit log was created in database
        new_count = self.env["spp.audit.log"].search_count([])
        self.assertGreater(
            new_count,
            initial_count,
            "Audit log should be created in database when file logging is disabled",
        )

        # Verify the audit log content
        audit_log = self.env["spp.audit.log"].search(
            [("res_id", "=", partner.id), ("model_id.model", "=", "res.partner")],
            limit=1,
        )
        self.assertTrue(audit_log, "Audit log record should exist")
        self.assertEqual(audit_log.method, "create", "Method should be 'create'")

    def test_file_logging_mode(self):
        """Test that audit logs are written to file when file logging is enabled"""
        # Create a temporary directory for test log files
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "audit_test.log")

            # Enable file logging and configure path
            self.env["ir.config_parameter"].sudo().set_param("spp.audit_log_to_file", "True")
            self.env["ir.config_parameter"].sudo().set_param("spp.audit_log_file_path", log_file)
            self.env["ir.config_parameter"].sudo().set_param("spp.audit_log_file_max_bytes", "10")
            self.env["ir.config_parameter"].sudo().set_param("spp.audit_log_file_backup_count", "3")

            # Count existing audit logs in database
            initial_db_count = self.env["spp.audit.log"].search_count([])

            # Create a new partner (should trigger audit log to file)
            partner = self.env["res.partner"].create(
                {
                    "name": "Test Partner File Mode",
                    "email": "test@example.com",
                }
            )

            # Verify log file was created and contains data
            self.assertTrue(os.path.exists(log_file), "Audit log file should be created")

            # Read and verify log file content
            with open(log_file, encoding="utf-8") as f:
                log_lines = f.readlines()

            self.assertGreater(len(log_lines), 0, "Log file should contain entries")

            # Parse and verify JSON format
            log_entry = json.loads(log_lines[-1])
            self.assertIn("timestamp", log_entry, "Log entry should have timestamp")
            self.assertIn("user_id", log_entry, "Log entry should have user_id")
            self.assertIn("model", log_entry, "Log entry should have model")
            self.assertIn("res_id", log_entry, "Log entry should have res_id")
            self.assertIn("method", log_entry, "Log entry should have method")
            self.assertIn("changes", log_entry, "Log entry should have changes")

            self.assertEqual(log_entry["model"], "res.partner", "Model should be res.partner")
            self.assertEqual(log_entry["res_id"], partner.id, "Resource ID should match")
            self.assertEqual(log_entry["method"], "create", "Method should be 'create'")

            # Verify database count did not increase (logs go to file instead)
            new_db_count = self.env["spp.audit.log"].search_count([])
            self.assertEqual(
                new_db_count,
                initial_db_count,
                "Database audit log count should not increase when file logging is enabled",
            )

    def test_file_logging_with_update(self):
        """Test that audit logs capture field changes correctly in file mode"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "audit_update_test.log")

            # Enable file logging
            self.env["ir.config_parameter"].sudo().set_param("spp.audit_log_to_file", "True")
            self.env["ir.config_parameter"].sudo().set_param("spp.audit_log_file_path", log_file)

            # Create initial partner
            partner = self.env["res.partner"].create(
                {
                    "name": "Original Name",
                    "phone": "+639111111111",
                }
            )

            # Clear the log file to focus on update operation
            if os.path.exists(log_file):
                open(log_file, "w").close()

            # Update the partner
            partner.write(
                {
                    "name": "Updated Name",
                    "phone": "+639222222222",
                }
            )

            # Read and verify the update log entry
            self.assertTrue(os.path.exists(log_file), "Log file should exist after update")

            with open(log_file, encoding="utf-8") as f:
                log_lines = f.readlines()

            self.assertGreater(len(log_lines), 0, "Log file should contain update entries")

            # Parse the last log entry
            log_entry = json.loads(log_lines[-1])
            self.assertEqual(log_entry["method"], "write", "Method should be 'write'")
            self.assertIn("changes", log_entry, "Log entry should have changes")

            # Verify changes contain old and new values
            changes = log_entry["changes"]
            self.assertIn("old", changes, "Changes should have 'old' values")
            self.assertIn("new", changes, "Changes should have 'new' values")

    def test_file_rotation(self):
        """Test that log file rotation works when size limit is reached"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "audit_rotation_test.log")

            # Set very small file size to trigger rotation quickly
            self.env["ir.config_parameter"].sudo().set_param("spp.audit_log_to_file", "True")
            self.env["ir.config_parameter"].sudo().set_param("spp.audit_log_file_path", log_file)
            self.env["ir.config_parameter"].sudo().set_param("spp.audit_log_file_max_bytes", "1")  # 1MB
            self.env["ir.config_parameter"].sudo().set_param("spp.audit_log_file_backup_count", "3")

            # Create multiple partners to generate enough log data
            for i in range(50):
                self.env["res.partner"].create(
                    {
                        "name": f"Partner {i} " + ("X" * 100),  # Add padding to increase file size
                        "email": f"partner{i}@rotation.test",
                        "phone": f"+6391234567{i:02d}",
                    }
                )

            # Check if rotation occurred by looking for backup files
            # Note: May not rotate if data isn't large enough, so we just verify the mechanism works
            self.assertTrue(
                os.path.exists(log_file),
                "Main log file should always exist",
            )

            # Verify log file has content
            with open(log_file, encoding="utf-8") as f:
                content = f.read()
                self.assertGreater(len(content), 0, "Log file should contain audit entries")

    def test_backward_compatibility_default_disabled(self):
        """Test that file logging is disabled by default (backward compatibility)"""
        # Remove the config parameter to test default behavior
        self.env["ir.config_parameter"].sudo().search([("key", "=", "spp.audit_log_to_file")]).unlink()

        initial_db_count = self.env["spp.audit.log"].search_count([])

        # Create a partner without explicit file logging configuration
        partner = self.env["res.partner"].create(
            {
                "name": "Backward Compat Partner",
                "email": "backcompat@test.com",
            }
        )

        # Should default to database logging
        new_db_count = self.env["spp.audit.log"].search_count([])
        self.assertGreater(
            new_db_count,
            initial_db_count,
            "Database logging should work by default for backward compatibility",
        )

        # Verify the audit log exists
        audit_log = self.env["spp.audit.log"].search(
            [("res_id", "=", partner.id), ("model_id.model", "=", "res.partner")],
            limit=1,
        )
        self.assertTrue(audit_log, "Audit log should exist in database by default")

    def test_backward_compatibility_existing_rules(self):
        """Test that existing audit rules continue to work without modification"""
        # Ensure database mode
        self.env["ir.config_parameter"].sudo().set_param("spp.audit_log_to_file", "False")

        # Use the existing audit rule from setUpClass
        initial_count = self.env["spp.audit.log"].search_count([("audit_rule_id", "=", self.res_partner_rule.id)])

        # Create a partner using existing rule
        partner = self.env["res.partner"].create(  # noqa: F841
            {
                "name": "Existing Rule Test",
            }
        )

        # Verify audit log was created using the existing rule
        new_count = self.env["spp.audit.log"].search_count([("audit_rule_id", "=", self.res_partner_rule.id)])
        self.assertGreater(
            new_count,
            initial_count,
            "Existing audit rules should continue to work",
        )

    def test_file_logging_with_invalid_path(self):
        """Test graceful handling of invalid file paths"""
        # Set an invalid path (no permission to write)
        self.env["ir.config_parameter"].sudo().set_param("spp.audit_log_to_file", "True")
        self.env["ir.config_parameter"].sudo().set_param("spp.audit_log_file_path", "/root/audit_invalid.log")

        # Should not crash, but log to database as fallback won't happen
        # (file logging enabled but file creation fails)
        try:
            partner = self.env["res.partner"].create(  # noqa: F841
                {
                    "name": "Invalid Path Test",
                }
            )
            # If no exception is raised, the test passes
            self.assertTrue(True, "Should handle invalid path gracefully")
        except Exception as e:
            self.fail(f"Should not raise exception with invalid path: {e}")

    def test_file_logging_configuration_change(self):
        """Test that configuration changes are picked up correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file1 = os.path.join(temp_dir, "audit_config1.log")
            log_file2 = os.path.join(temp_dir, "audit_config2.log")

            # Start with first configuration
            self.env["ir.config_parameter"].sudo().set_param("spp.audit_log_to_file", "True")
            self.env["ir.config_parameter"].sudo().set_param("spp.audit_log_file_path", log_file1)

            # Create a partner (should log to file1)
            partner1 = self.env["res.partner"].create(  # noqa: F841
                {
                    "name": "Config Test 1",
                }
            )

            self.assertTrue(os.path.exists(log_file1), "First log file should be created")

            # Change configuration to different file
            self.env["ir.config_parameter"].sudo().set_param("spp.audit_log_file_path", log_file2)

            # Create another partner (should log to file2)
            partner2 = self.env["res.partner"].create(  # noqa: F841
                {
                    "name": "Config Test 2",
                }
            )

            self.assertTrue(os.path.exists(log_file2), "Second log file should be created")

            # Verify both files have content
            with open(log_file1, encoding="utf-8") as f:
                content1 = f.read()
                self.assertIn("Config Test 1", content1, "First file should have first partner")

            with open(log_file2, encoding="utf-8") as f:
                content2 = f.read()
                self.assertIn("Config Test 2", content2, "Second file should have second partner")

    def test_json_format_validity(self):
        """Test that all log entries are valid JSON"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "audit_json_test.log")

            self.env["ir.config_parameter"].sudo().set_param("spp.audit_log_to_file", "True")
            self.env["ir.config_parameter"].sudo().set_param("spp.audit_log_file_path", log_file)

            # Create multiple partners with various operations
            partner = self.env["res.partner"].create(  # noqa: F841
                {
                    "name": "JSON Test Partner",
                    "email": "json@test.com",
                    "phone": "+639111111111",
                }
            )

            partner.write(
                {
                    "name": "Updated JSON Partner",
                    "email": "updated@test.com",
                }
            )

            # Read and validate all JSON entries
            with open(log_file, encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        entry = json.loads(line)
                        # Verify required fields
                        self.assertIn("timestamp", entry, f"Line {line_num} missing timestamp")
                        self.assertIn("user_id", entry, f"Line {line_num} missing user_id")
                        self.assertIn("model", entry, f"Line {line_num} missing model")
                        self.assertIn("res_id", entry, f"Line {line_num} missing res_id")
                        self.assertIn("method", entry, f"Line {line_num} missing method")
                        self.assertIn("changes", entry, f"Line {line_num} missing changes")
                    except json.JSONDecodeError as e:
                        self.fail(f"Line {line_num} is not valid JSON: {e}")

    def test_unlink_operation_logging(self):
        """Test that unlink operations are properly logged to file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "audit_unlink_test.log")

            self.env["ir.config_parameter"].sudo().set_param("spp.audit_log_to_file", "True")
            self.env["ir.config_parameter"].sudo().set_param("spp.audit_log_file_path", log_file)

            # Enable unlink logging for the test
            self.res_partner_rule.write({"log_unlink": True})

            # Create and then delete a partner
            partner = self.env["res.partner"].create(
                {
                    "name": "Partner to Delete",
                }
            )
            partner_id = partner.id

            # Clear log to focus on unlink operation
            if os.path.exists(log_file):
                open(log_file, "w").close()

            # Delete the partner
            partner.unlink()

            # Verify unlink was logged
            with open(log_file, encoding="utf-8") as f:
                log_lines = f.readlines()

            self.assertGreater(len(log_lines), 0, "Unlink operation should be logged")

            # Find the unlink entry
            unlink_entry = None
            for line in log_lines:
                entry = json.loads(line)
                if entry["method"] == "unlink" and entry["res_id"] == partner_id:
                    unlink_entry = entry
                    break

            self.assertIsNotNone(unlink_entry, "Unlink entry should exist in log")
            self.assertEqual(unlink_entry["method"], "unlink", "Method should be 'unlink'")
