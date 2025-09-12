import logging
from unittest.mock import patch

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestChangeRequestBase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create test users
        cls.user_admin = cls.env.ref("base.user_admin")
        cls.user_demo = cls.env["res.users"].create(
            {
                "name": "Test User",
                "login": "test_user",
                "password": "test_password",
            }
        )

        # Create test registrants
        cls.registrant_1 = cls.env["res.partner"].create(
            {
                "name": "Test Partner 1",
                "phone": "+639171234567",
                "is_registrant": True,
                "country_id": cls.env.ref("base.ph").id,
            }
        )
        cls.registrant_2 = cls.env["res.partner"].create(
            {
                "name": "Test Partner 2",
                "phone": "+639171234568",
                "is_registrant": True,
                "is_group": True,
                "country_id": cls.env.ref("base.ph").id,
            }
        )
        cls.validation_ids = []

        # Patch to allow creating spp.change.request
        patcher = patch(
            "odoo.addons.spp_change_request_base.models.change_request.ChangeRequestBase._selection_request_type_ref_id"
        )
        mock_selection = patcher.start()
        mock_selection.return_value = [("test.cr.type2", "Test CR Type")]
        mock_selection.__name__ = "_mocked__selection_request_type_ref_id"
        cls.addClassCleanup(patcher.stop)

    def _create_test_cr(self):
        default_vals = {
            "request_type": "test.cr.type2",
            "registrant_id": self.registrant_1.id,
            "applicant_phone": "+639171234567",
        }

        return self.env["spp.change.request"].create(default_vals)

    def test_01_cr_creation(self):
        """Test change request creation with default values"""
        change_request = self._create_test_cr()
        self.assertTrue(change_request.name)
        self.assertEqual(change_request.assign_to_id, self.env.user)
        self.assertEqual(change_request.request_type, "test.cr.type2")

    def test_02_onchange_request_type(self):
        """Test that registrant_id is cleared when request_type changes."""
        change_request = self._create_test_cr()
        self.assertEqual(change_request.registrant_id, self.registrant_1)

        # Simulate onchange
        change_request._onchange_request_type()

        self.assertFalse(change_request.registrant_id)

    def test_03_onchange_registrant_id(self):
        """Test that applicant_id and applicant_phone are cleared when registrant_id changes."""
        change_request = self._create_test_cr()
        change_request.applicant_id = self.registrant_1.id
        self.assertTrue(change_request.applicant_id)
        self.assertTrue(change_request.applicant_phone)

        change_request.registrant_id = self.registrant_2.id
        change_request._onchange_registrant_id()

        self.assertFalse(change_request.applicant_id)
        self.assertFalse(change_request.applicant_phone)

    def test_04_onchange_applicant_id(self):
        """Test that applicant_phone is updated when applicant_id changes."""
        change_request = self._create_test_cr()
        change_request.applicant_id = self.registrant_1.id
        change_request._onchange_applicant_id()
        self.assertEqual(change_request.applicant_phone, self.registrant_1.phone)

        change_request.applicant_id = False
        change_request._onchange_applicant_id()
        self.assertFalse(change_request.applicant_phone)

    def test_05_check_applicant_phone(self):
        """Test applicant phone number validation."""
        change_request = self._create_test_cr()
        with self.assertRaises(ValidationError):
            change_request.applicant_phone = "invalid phone"
            change_request._check_applicant_phone()

        # Should not raise error
        change_request.applicant_phone = "+639171234567"
        change_request._check_applicant_phone()

    def test_06_open_applicant_form(self):
        """Test opening applicant form view."""
        change_request = self._create_test_cr()
        # No applicant
        action = change_request.open_applicant_form()
        self.assertEqual(action["type"], "ir.actions.client")
        self.assertEqual(action["tag"], "display_notification")

        # With applicant
        change_request.applicant_id = self.registrant_1.id
        action = change_request.open_applicant_form()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "res.partner")
        self.assertEqual(action["res_id"], self.registrant_1.id)

    def test_07_check_phone_exist(self):
        """Test _check_phone_exist method."""
        change_request = self._create_test_cr()
        change_request.applicant_phone_required = True
        change_request.applicant_phone = False
        with self.assertRaises(UserError) as e:
            change_request._check_phone_exist()
        self.assertEqual(str(e.exception), "Phone No. is required.")

        change_request.applicant_phone = "+639171234567"
        self.assertIsNone(change_request._check_phone_exist())

    def test_08_approve_cr(self):
        """Test approve_cr method."""
        change_request = self._create_test_cr()
        with self.assertRaises(ValidationError):
            change_request.with_user(self.user_demo).approve_cr()

        test_cr_type_record = self.env["test.cr.type2"].create(
            {
                "change_request_id": change_request.id,
            }
        )

        change_request.request_type_ref_id = test_cr_type_record
        self.user_demo.groups_id = [(4, self.env.ref("spp_change_request.group_spp_change_request_external_api").id)]
        change_request.with_user(self.user_demo).approve_cr()
        self.assertEqual(change_request.state, "applied")

    def test_09_action_cancel(self):
        """Test action_cancel method."""
        change_request = self._create_test_cr()
        action = change_request.action_cancel()
        self.assertEqual(action["res_model"], "spp.change.request.cancel.wizard")
        self.assertEqual(action["context"]["change_request_id"], change_request.id)

    def test_10_action_reject(self):
        """Test action_reject method."""
        change_request = self._create_test_cr()
        action = change_request.action_reject()
        self.assertEqual(action["res_model"], "spp.change.request.reject.wizard")
