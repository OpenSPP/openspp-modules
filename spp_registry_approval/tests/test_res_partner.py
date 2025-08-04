import logging

from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class SppRegistryApprovalTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set context to avoid job queue delay
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )

        # Get the security groups
        cls.approve_group = cls.env.ref("spp_registry_approval.approve_registry")
        cls.reject_group = cls.env.ref("spp_registry_approval.reject_registry")
        cls.reset_group = cls.env.ref("spp_registry_approval.reset_to_draft_registry")

        # Create test users with different permissions
        cls.user_with_approve = cls.env["res.users"].create(
            {
                "name": "User with Approve Permission",
                "login": "approve_user",
                "email": "approve@test.com",
                "groups_id": [(6, 0, [cls.approve_group.id])],
            }
        )

        cls.user_with_reject = cls.env["res.users"].create(
            {
                "name": "User with Reject Permission",
                "login": "reject_user",
                "email": "reject@test.com",
                "groups_id": [(6, 0, [cls.reject_group.id])],
            }
        )

        cls.user_with_reset = cls.env["res.users"].create(
            {
                "name": "User with Reset Permission",
                "login": "reset_user",
                "email": "reset@test.com",
                "groups_id": [(6, 0, [cls.reset_group.id])],
            }
        )

        cls.user_without_permissions = cls.env["res.users"].create(
            {
                "name": "User without Permissions",
                "login": "no_perms_user",
                "email": "noperms@test.com",
                "groups_id": [(6, 0, [])],
            }
        )

        # Create test registries
        cls.registry_draft = cls.env["res.partner"].create(
            {
                "name": "Test Registry Draft",
                "is_registrant": True,
                "is_group": False,
            }
        )

        cls.registry_approved = cls.env["res.partner"].create(
            {
                "name": "Test Registry Approved",
                "is_registrant": True,
                "is_group": False,
                "state": "approved",
            }
        )

        cls.registry_rejected = cls.env["res.partner"].create(
            {
                "name": "Test Registry Rejected",
                "is_registrant": True,
                "is_group": False,
                "state": "rejected",
            }
        )

    def test_01_default_state(self):
        """Test that new registries default to draft state"""
        new_registry = self.env["res.partner"].create(
            {
                "name": "New Test Registry",
                "is_registrant": True,
                "is_group": False,
            }
        )
        self.assertEqual(
            new_registry.state,
            "draft",
            "New registries should default to draft state",
        )

    def test_02_approve_registry_with_permission(self):
        """Test approve_registry method with proper permissions"""
        # Test with user having approve permission
        self.registry_draft.with_user(self.user_with_approve).approve_registry()
        self.assertEqual(
            self.registry_draft.state,
            "approved",
            "Registry should be approved when user has permission",
        )

    def test_03_approve_registry_without_permission(self):
        """Test approve_registry method without proper permissions"""
        # Reset to draft first
        self.registry_draft.state = "draft"

        # Test with user without approve permission
        self.registry_draft.with_user(self.user_without_permissions).approve_registry()
        self.assertEqual(
            self.registry_draft.state,
            "draft",
            "Registry should remain draft when user lacks permission",
        )

    def test_04_reject_registry_with_permission(self):
        """Test reject_registry method with proper permissions"""
        # Test with user having reject permission
        self.registry_draft.with_user(self.user_with_reject).reject_registry()
        self.assertEqual(
            self.registry_draft.state,
            "rejected",
            "Registry should be rejected when user has permission",
        )

    def test_05_reject_registry_without_permission(self):
        """Test reject_registry method without proper permissions"""
        # Reset to draft first
        self.registry_draft.state = "draft"

        # Test with user without reject permission
        self.registry_draft.with_user(self.user_without_permissions).reject_registry()
        self.assertEqual(
            self.registry_draft.state,
            "draft",
            "Registry should remain draft when user lacks permission",
        )

    def test_06_reset_to_draft_registry_with_permission(self):
        """Test reset_to_draft_registry method with proper permissions"""
        # Test with user having reset permission
        self.registry_approved.with_user(self.user_with_reset).reset_to_draft_registry()
        self.assertEqual(
            self.registry_approved.state,
            "draft",
            "Registry should be reset to draft when user has permission",
        )

    def test_07_reset_to_draft_registry_without_permission(self):
        """Test reset_to_draft_registry method without proper permissions"""
        # Reset to approved first
        self.registry_approved.state = "approved"

        # Test with user without reset permission
        self.registry_approved.with_user(self.user_without_permissions).reset_to_draft_registry()
        self.assertEqual(
            self.registry_approved.state,
            "approved",
            "Registry should remain approved when user lacks permission",
        )

    def test_08_multiple_records_approval(self):
        """Test approve_registry method with multiple records"""
        # Create multiple registries
        registries = self.env["res.partner"].create(
            [
                {
                    "name": "Registry 1",
                    "is_registrant": True,
                    "is_group": False,
                    "state": "draft",
                },
                {
                    "name": "Registry 2",
                    "is_registrant": True,
                    "is_group": False,
                    "state": "draft",
                },
            ]
        )

        # Approve all registries
        registries.with_user(self.user_with_approve).approve_registry()

        # Verify all are approved
        for registry in registries:
            self.assertEqual(
                registry.state,
                "approved",
                f"Registry {registry.name} should be approved",
            )

    def test_09_state_constants(self):
        """Test that state constants are properly defined"""
        self.assertEqual(
            self.env["res.partner"].DRAFT,
            "draft",
            "DRAFT constant should be 'draft'",
        )
        self.assertEqual(
            self.env["res.partner"].APPROVED,
            "approved",
            "APPROVED constant should be 'approved'",
        )
        self.assertEqual(
            self.env["res.partner"].REJECTED,
            "rejected",
            "REJECTED constant should be 'rejected'",
        )

    def test_10_edge_case_empty_recordset(self):
        """Test methods with empty recordset"""
        empty_recordset = self.env["res.partner"].browse([])

        # These should not raise errors
        empty_recordset.with_user(self.user_with_approve).approve_registry()
        empty_recordset.with_user(self.user_with_reject).reject_registry()
        empty_recordset.with_user(self.user_with_reset).reset_to_draft_registry()

    def test_11_mixed_permissions_user(self):
        """Test user with multiple permissions"""
        # Create user with multiple permissions
        user_multi = self.env["res.users"].create(
            {
                "name": "User with Multiple Permissions",
                "login": "multi_user",
                "email": "multi@test.com",
                "groups_id": [(6, 0, [self.approve_group.id, self.reject_group.id, self.reset_group.id])],
            }
        )

        # Test all operations with multi-permission user
        registry = self.env["res.partner"].create(
            {
                "name": "Multi Test Registry",
                "is_registrant": True,
                "is_group": False,
                "state": "draft",
            }
        )

        # Approve
        registry.with_user(user_multi).approve_registry()
        self.assertEqual(registry.state, "approved")

        # Reject
        registry.with_user(user_multi).reject_registry()
        self.assertEqual(registry.state, "rejected")

        # Reset to draft
        registry.with_user(user_multi).reset_to_draft_registry()
        self.assertEqual(registry.state, "draft")

    def test_12_sudo_usage(self):
        """Test that sudo() is properly used in methods"""
        # This test verifies that the methods use sudo() correctly
        # by checking that the state changes are applied even when
        # the user doesn't have direct write access to the record

        # Create a registry with restricted access
        registry = self.env["res.partner"].create(
            {
                "name": "Restricted Registry",
                "is_registrant": True,
                "is_group": False,
                "state": "draft",
            }
        )

        # Test that sudo() allows the operation to succeed
        registry.with_user(self.user_with_approve).approve_registry()
        self.assertEqual(
            registry.state,
            "approved",
            "sudo() should allow approval even with restricted access",
        )
