from odoo.tests.common import TransactionCase


class AuditPostChatterTest(TransactionCase):
    """Test that chatter messages are skipped when file logging is enabled"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Get or create res.partner model
        cls.model_partner = cls.env["ir.model"].search([("model", "=", "res.partner")], limit=1)

        # Get name field for res.partner
        cls.field_name = cls.env["ir.model.fields"].search(
            [("model_id", "=", cls.model_partner.id), ("name", "=", "name")], limit=1
        )

        # Create audit rule for res.partner
        cls.audit_rule = cls.env["spp.audit.rule"].create(
            {
                "name": "Test Partner Audit Rule",
                "model_id": cls.model_partner.id,
                "log_create": True,
                "log_write": True,
                "log_unlink": False,
                "field_to_log_ids": [(6, 0, [cls.field_name.id])],
            }
        )

        # Register the audit rule hook
        cls.env["spp.audit.rule"]._register_hook([cls.audit_rule.id])

    def test_chatter_enabled_in_database_mode(self):
        """Test that chatter messages are posted when database logging is enabled"""
        # Disable file logging (use database mode)
        self.env["ir.config_parameter"].sudo().set_param("spp.audit_log_to_file", "False")

        # Create a partner (this should create audit log and post to chatter)
        partner = self.env["res.partner"].create(
            {
                "name": "Test Partner for Chatter",
                "email": "chatter@test.com",
            }
        )

        # Check that an audit log was created in database
        audit_log = self.env["spp.audit.log"].search(
            [
                ("res_id", "=", partner.id),
                ("model_id", "=", self.model_partner.id),
                ("method", "=", "create"),
            ],
            limit=1,
        )
        self.assertTrue(audit_log, "Audit log should exist in database mode")

        # Check that a message was posted to chatter
        messages = partner.message_ids.filtered(lambda m: m.message_type == "notification")
        self.assertTrue(
            messages,
            "At least one chatter message should be posted in database mode",
        )

    def test_chatter_disabled_in_file_mode(self):
        """Test that chatter messages are NOT posted when file logging is enabled"""
        # Enable file logging
        self.env["ir.config_parameter"].sudo().set_param("spp.audit_log_to_file", "True")
        self.env["ir.config_parameter"].sudo().set_param("spp.audit_log_file_path", "/tmp/audit_chatter_test.log")

        # Create a partner (this should NOT post to chatter)
        partner = self.env["res.partner"].create(
            {
                "name": "Test Partner No Chatter",
                "email": "nochatter@test.com",
            }
        )

        # Check that NO audit log was created in database (goes to file instead)
        audit_log_count = self.env["spp.audit.log"].search_count(
            [
                ("res_id", "=", partner.id),
                ("model_id", "=", self.model_partner.id),
                ("method", "=", "create"),
            ]
        )
        self.assertEqual(
            audit_log_count,
            0,
            "No audit log should exist in database when file logging is enabled",
        )

        # Get initial message count (may have system messages)
        initial_message_count = len(partner.message_ids)

        # Update the partner to trigger audit
        partner.write({"name": "Updated Name"})

        # Check that no new messages were posted to chatter
        new_message_count = len(partner.message_ids)
        self.assertEqual(
            new_message_count,
            initial_message_count,
            "No new chatter messages should be posted when file logging is enabled",
        )

    def test_chatter_with_parent_rule_file_mode(self):
        """Test that parent audit logs don't post to chatter when file logging is enabled"""
        # Enable file logging
        self.env["ir.config_parameter"].sudo().set_param("spp.audit_log_to_file", "True")

        # Create a parent partner (group)
        parent_partner = self.env["res.partner"].create(
            {
                "name": "Parent Partner",
                "is_company": True,
            }
        )

        initial_parent_message_count = len(parent_partner.message_ids)

        # Create a child partner with parent relationship
        child_partner = self.env["res.partner"].create(
            {
                "name": "Child Partner",
                "parent_id": parent_partner.id,
            }
        )

        # Update child partner
        child_partner.write({"name": "Updated Child Partner"})

        # Verify parent didn't receive chatter messages
        new_parent_message_count = len(parent_partner.message_ids)
        self.assertEqual(
            new_parent_message_count,
            initial_parent_message_count,
            "Parent should not receive chatter messages when file logging is enabled",
        )

    def test_mode_switching(self):
        """Test that switching between modes works correctly"""
        partner = self.env["res.partner"].create(
            {
                "name": "Mode Switching Partner",
            }
        )

        # Start with database mode
        self.env["ir.config_parameter"].sudo().set_param("spp.audit_log_to_file", "False")
        initial_message_count = len(partner.message_ids)

        # Update in database mode (should post to chatter)
        partner.write({"name": "Update in DB Mode"})
        db_mode_message_count = len(partner.message_ids)
        self.assertGreater(
            db_mode_message_count,
            initial_message_count,
            "Chatter message should be posted in database mode",
        )

        # Switch to file mode
        self.env["ir.config_parameter"].sudo().set_param("spp.audit_log_to_file", "True")
        self.env["ir.config_parameter"].sudo().set_param("spp.audit_log_file_path", "/tmp/audit_mode_switch.log")

        # Update in file mode (should NOT post to chatter)
        partner.write({"name": "Update in File Mode"})
        file_mode_message_count = len(partner.message_ids)
        self.assertEqual(
            file_mode_message_count,
            db_mode_message_count,
            "No new chatter message should be posted in file mode",
        )
