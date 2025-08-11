from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestG2PGroupMembership(TransactionCase):
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

        # Create test data
        cls.individual_1 = cls.env["res.partner"].create(
            {
                "name": "Test Individual 1",
                "is_group": False,
                "is_registrant": True,
            }
        )
        cls.individual_2 = cls.env["res.partner"].create(
            {
                "name": "Test Individual 2",
                "is_group": False,
                "is_registrant": True,
            }
        )
        cls.group = cls.env["res.partner"].create(
            {
                "name": "Test Group",
                "is_group": True,
                "is_registrant": True,
            }
        )

        # Get the head membership kind
        cls.head_kind = cls.env.ref("g2p_registry_membership.group_membership_kind_head")

        # Create memberships
        cls.membership_1 = cls.env["g2p.group.membership"].create(
            {
                "group": cls.group.id,
                "individual": cls.individual_1.id,
                "kind": [(4, cls.head_kind.id)],
            }
        )
        cls.membership_2 = cls.env["g2p.group.membership"].create(
            {
                "group": cls.group.id,
                "individual": cls.individual_2.id,
            }
        )

    def test_01_unlink_non_head_member(self):
        """Test unlink of a non-head member"""
        # Should be able to unlink non-head member
        self.membership_2.unlink()
        self.assertFalse(self.membership_2.exists())

    def test_02_unlink_head_member_with_skip_context(self):
        """Test unlink of head member with skip_head_check context"""
        # Should be able to unlink head member with skip context
        self.membership_1.with_context(skip_head_check=True).unlink()
        self.assertFalse(self.membership_1.exists())
