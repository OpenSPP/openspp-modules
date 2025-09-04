import logging
from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestChangeRequestBase(TransactionCase):
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
                "phone": "+1234567890",
            }
        )
        cls.registrant_2 = cls.env["res.partner"].create(
            {
                "name": "Test Partner 2",
                "phone": "+0987654321",
            }
        )

    @patch("odoo.addons.spp_change_request_base.models.change_request.ChangeRequestBase._selection_request_type_ref_id")
    def _create_test_change_request(self, mock_request_type_selection, **kwargs):
        """Helper method to create a test change request"""
        mock_request_type_selection.return_value = [("test.request.type", "Test Request Type")]
        mock_request_type_selection.__name__ = "_mocked__selection_request_type_ref_id"

        default_vals = {
            "name": "Test Request",
            "request_type": "test.request.type",
            "registrant_id": self.registrant_1.id,
        }
        default_vals.update(kwargs)
        return self.env["spp.change.request"].create(default_vals)

    def test_01_change_request_creation(self):
        """Test change request creation with default values"""
        change_request = self._create_test_change_request()

        self.assertEqual(change_request.state, "draft")
        self.assertEqual(change_request.assign_to_id, self.env.user)
        self.assertIsNotNone(change_request.date_requested)
        self.assertEqual(change_request.request_type, "test.request.type")

    def test_02_change_request_unlink_draft(self):
        """Test that draft change requests can be deleted by creator"""
        change_request = self._create_test_change_request()
        change_request.unlink()

        # Verify it's deleted
        self.assertFalse(change_request.exists())

    def test_03_change_request_unlink_non_draft_error(self):
        """Test that non-draft change requests cannot be deleted"""
        change_request = self._create_test_change_request()
        change_request.state = "pending"

        with self.assertRaises(UserError):
            change_request.unlink()

    def test_04_change_request_unlink_wrong_user_error(self):
        """Test that change requests cannot be deleted by non-creator"""
        change_request = self._create_test_change_request()

        with self.assertRaises(UserError):
            change_request.with_user(self.user_demo).unlink()

    def test_05_assign_to_user(self):
        """Test assigning change request to user"""
        change_request = self._create_test_change_request()

        # Test assignment
        change_request.assign_to_user(self.user_demo)
        self.assertEqual(change_request.assign_to_id, self.user_demo)

    def test_06_assign_to_user_pending_state_error(self):
        """Test assignment error when in pending state without validation sequence"""
        change_request = self._create_test_change_request()
        change_request.state = "pending"

        with self.assertRaises(UserError):
            change_request.assign_to_user(self.user_demo)

    def test_07_onchange_request_type(self):
        """Test that registrant_id is cleared when request_type changes."""
        change_request = self._create_test_change_request()
        self.assertEqual(change_request.registrant_id, self.registrant_1)

        # Simulate onchange
        change_request._onchange_request_type()

        self.assertFalse(change_request.registrant_id)

    def test_08_open_change_request_form_no_ref_id(self):
        """Test opening form without a request_type_ref_id returns a notification."""
        change_request = self._create_test_change_request()
        action = change_request.open_change_request_form()

        self.assertEqual(action["type"], "ir.actions.client")
        self.assertEqual(action["tag"], "display_notification")
        self.assertEqual(action["params"]["type"], "danger")
        self.assertEqual(action["params"]["message"], "The Request Type field must be filled-up.")

    def test_09_action_submit_no_ref_id_error(self):
        """Test submitting a CR without a request_type_ref_id raises an error."""
        change_request = self._create_test_change_request()

        with self.assertRaises(UserError) as e:
            change_request.action_submit()
        self.assertEqual(str(e.exception), "The change request type must be properly filled-up.")

    def test_10_create_request_detail_not_draft_or_pending_error(self):
        """Test creating request detail for a CR not in draft or pending state raises an error."""
        change_request = self._create_test_change_request(state="applied")

        with self.assertRaises(UserError) as e:
            change_request.create_request_detail()
        self.assertEqual(
            str(e.exception), "The change request to be created must be in draft or pending validation state."
        )

    def test_11_cancel_cr_not_in_allowed_state_error(self):
        """Test that cancelling a CR not in draft, pending, or rejected state raises an error."""
        change_request = self._create_test_change_request(state="applied")

        with self.assertRaises(UserError) as e:
            change_request._cancel(change_request)
        self.assertEqual(
            str(e.exception), "The request to be cancelled must be in draft, pending, or rejected validation state."
        )

    def test_12_cancel_cr_in_draft_state(self):
        """Test cancelling a CR in draft state."""
        change_request = self._create_test_change_request()
        change_request._cancel(change_request)

        self.assertEqual(change_request.state, "cancelled")
        self.assertEqual(change_request.cancelled_by_id, self.env.user)
        self.assertIsNotNone(change_request.date_cancelled)

    def test_13_check_user_not_assigned_error(self):
        """Test _check_user when no user is assigned raises an error."""
        change_request = self._create_test_change_request(assign_to_id=False)

        with self.assertRaises(UserError) as e:
            change_request._check_user("validate")
        self.assertEqual(str(e.exception), "There are no user assigned to this change request.")

    def test_14_check_user_wrong_user_error(self):
        """Test _check_user when a different user tries to process raises an error."""
        change_request = self._create_test_change_request(assign_to_id=self.user_demo.id)

        with self.assertRaises(UserError) as e:
            change_request.with_user(self.user_admin)._check_user("validate")
        self.assertEqual(str(e.exception), "You are not allowed to validate this change request")

    def test_15_check_user_correct_user(self):
        """Test _check_user with the correct assigned user."""
        change_request = self._create_test_change_request(assign_to_id=self.user_demo.id)

        result = change_request.with_user(self.user_demo)._check_user("validate")
        self.assertTrue(result)
