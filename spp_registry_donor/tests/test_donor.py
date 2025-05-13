from ast import literal_eval

from odoo.exceptions import AccessError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestDonorRegistry(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create users with different access levels
        cls.donor_user = cls.env["res.users"].create(
            {
                "name": "Donor User",
                "login": "donor_user",
                "email": "donor@test.com",
                "groups_id": [
                    (4, cls.env.ref("spp_registry_donor.group_donor_user").id),
                    (4, cls.env.ref("base.group_user").id),  # Internal User group
                ],
            }
        )

        cls.donor_manager = cls.env["res.users"].create(
            {
                "name": "Donor Manager",
                "login": "donor_manager",
                "email": "donor_manager@test.com",
                "groups_id": [
                    (4, cls.env.ref("spp_registry_donor.group_donor_manager").id),
                    (4, cls.env.ref("base.group_user").id),  # Internal User group
                ],
            }
        )

        # Create test partners
        cls.donor = cls.env["res.partner"].create(
            {
                "name": "Test Donor",
                "is_donor": True,
                "email": "test.donor@example.com",
            }
        )

        cls.non_donor = cls.env["res.partner"].create(
            {
                "name": "Non Donor Partner",
                "is_donor": False,
                "email": "non.donor@example.com",
            }
        )

    def test_01_donor_creation(self):
        """Test donor creation and fields"""
        self.assertTrue(self.donor.is_donor, "Partner should be marked as donor")
        self.assertFalse(self.non_donor.is_donor, "Partner should not be marked as donor")

    def test_02_donor_user_access(self):
        """Test donor user access rights"""
        # Switch to donor user
        donor_user_env = self.env["res.partner"].with_user(self.donor_user)

        # Should be able to read donor records
        donor = donor_user_env.browse(self.donor.id)
        self.assertEqual(donor.name, "Test Donor", "Donor user should be able to read donor records")

        # Should not be able to create/write/unlink donor records
        with self.assertRaises(AccessError):
            donor_user_env.create(
                {
                    "name": "New Donor",
                    "is_donor": True,
                }
            )

        with self.assertRaises(AccessError):
            donor.write({"name": "Updated Name"})

        with self.assertRaises(AccessError):
            donor.unlink()

    def test_03_donor_manager_access(self):
        """Test donor manager access rights"""
        # Switch to donor manager
        manager_env = self.env["res.partner"].with_user(self.donor_manager)

        # Should be able to create donor
        new_donor = manager_env.create(
            {
                "name": "New Donor by Manager",
                "is_donor": True,
                "email": "new.donor@example.com",
            }
        )
        self.assertTrue(new_donor.is_donor, "Manager should be able to create donors")

        # Should be able to update donor
        new_donor.write({"name": "Updated Donor Name"})
        self.assertEqual(new_donor.name, "Updated Donor Name", "Manager should be able to update donors")

        # Should be able to delete donor
        new_donor.unlink()
        self.assertFalse(manager_env.search([("id", "=", new_donor.id)]), "Manager should be able to delete donors")

    def test_04_action_window(self):
        """Test the donor action window"""
        action = self.env["ir.actions.act_window"]._for_xml_id("spp_registry_donor.action_registry_donor")

        # Check action configuration
        self.assertEqual(action["res_model"], "res.partner", "Action should target res.partner model")

        # Convert domain string to list using ast.literal_eval if needed
        domain = action["domain"]
        if isinstance(domain, str):
            domain = literal_eval(domain)
        self.assertEqual(domain, [("is_donor", "=", True)], "Action should filter donors only")

        self.assertIn("default_is_donor", action["context"], "Action should set default donor context")

    def test_05_menu_access(self):
        """Test menu access rights"""
        menu = self.env.ref("spp_registry_donor.menu_registry_donor")

        # Add necessary groups for menu access
        self.donor_user.write(
            {
                "groups_id": [
                    (4, self.env.ref("base.group_user").id),
                    (4, self.env.ref("g2p_registry_base.group_g2p_registrar").id),
                ]
            }
        )

        # Donor user should see the menu
        menu_visible = menu.with_user(self.donor_user).check_access_rights("read", raise_exception=False)
        self.assertTrue(menu_visible, "Donor user should see the donors menu")

        # Create a regular user without donor access
        regular_user = self.env["res.users"].create(
            {
                "name": "Regular User",
                "login": "regular_user",
                "email": "regular@test.com",
                "groups_id": [(4, self.env.ref("base.group_user").id)],
            }
        )

        # Regular user should not see the menu
        menu_visible = menu.with_user(regular_user).check_access_rights("read", raise_exception=False)
        self.assertFalse(menu_visible, "Regular user should not see the donors menu")
