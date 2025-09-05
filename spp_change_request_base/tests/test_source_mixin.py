from unittest.mock import patch

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestChangeRequestSourceMixin(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user_admin = cls.env.ref("base.user_admin")
        cls.user_demo = cls.env["res.users"].create(
            {
                "name": "Test User",
                "login": "test_user",
            }
        )

        # Patch to allow creating spp.change.request
        patcher = patch(
            "odoo.addons.spp_change_request_base.models.change_request.ChangeRequestBase._selection_request_type_ref_id"
        )
        mock_selection = patcher.start()
        mock_selection.return_value = [("test.cr.type", "Test CR Type")]
        mock_selection.__name__ = "_mocked__selection_request_type_ref_id"
        cls.addClassCleanup(patcher.stop)

    def setUp(self):
        super().setUp()
        self.change_request = self.env["spp.change.request"].create(
            {
                "name": "Test CR",
                "request_type": "test.cr.type",
            }
        )

        self.test_cr_type_record = self.env["test.cr.type"].create(
            {
                "change_request_id": self.change_request.id,
            }
        )

    def test_update_live_data_not_implemented(self):
        """Test that update_live_data raises NotImplementedError."""
        # We create a fresh record that will use the default implementation
        test_record = self.env["test.cr.type"].new()
        with self.assertRaises(NotImplementedError):
            test_record.update_live_data()

    def test_on_submit_draft_state(self):
        """Test _on_submit when the request is in 'draft' state."""
        dms_directory = self.env["spp.dms.directory"].create({"name": "Test Directory"})
        self.change_request.dms_directory_ids = [(4, dms_directory.id)]
        self.assertEqual(self.change_request.state, "draft")
        self.test_cr_type_record._on_submit(self.change_request)
        self.assertEqual(self.change_request.state, "pending")
        self.assertIsNotNone(self.change_request.date_requested)

    def test_on_submit_not_draft_state_error(self):
        """Test _on_submit raises ValidationError if not in 'draft' state."""
        self.change_request.state = "pending"
        with self.assertRaises(ValidationError) as e:
            self.test_cr_type_record._on_submit(self.change_request)
        self.assertEqual(str(e.exception), "The request must be in draft state to be set to pending validation.")

    def test_apply_not_validated_state_error(self):
        """Test _apply raises ValidationError if not in 'validated' state."""
        self.change_request.state = "pending"
        with self.assertRaises(ValidationError) as e:
            self.test_cr_type_record._apply(self.change_request)
        self.assertEqual(str(e.exception), "The request must be in validated state for changes to be applied.")

    def test_apply_success(self):
        """Test _apply success path."""
        self.change_request.state = "validated"
        self.change_request.assign_to_id = self.env.user

        # Mock update_live_data to avoid NotImplementedError and check it's called
        with patch.object(type(self.test_cr_type_record), "update_live_data") as mock_update:
            self.test_cr_type_record._apply(self.change_request)
            mock_update.assert_called_once()

        self.assertEqual(self.change_request.state, "applied")
        self.assertEqual(self.change_request.applied_by_id, self.env.user)
        self.assertIsNotNone(self.change_request.date_applied)

    def test_cancel_in_valid_state(self):
        """Test _cancel when request is in a cancellable state."""
        self.change_request.state = "pending"
        self.test_cr_type_record._cancel(self.change_request)
        self.assertEqual(self.change_request.state, "cancelled")
        self.assertEqual(self.change_request.cancelled_by_id, self.env.user)
        self.assertIsNotNone(self.change_request.date_cancelled)

    def test_cancel_in_invalid_state_error(self):
        """Test _cancel raises UserError if in a non-cancellable state."""
        self.change_request.state = "applied"
        with self.assertRaises(UserError) as e:
            self.test_cr_type_record._cancel(self.change_request)
        self.assertEqual(
            str(e.exception), "The request to be cancelled must be in draft, pending, or rejected validation state."
        )

    def test_reset_to_draft_in_rejected_state(self):
        """Test _reset_to_draft when request is in 'rejected' state."""
        self.change_request.state = "rejected"
        self.test_cr_type_record._reset_to_draft(self.change_request)
        self.assertEqual(self.change_request.state, "draft")
        self.assertEqual(self.change_request.reset_to_draft_by_id, self.env.user)

    def test_reset_to_draft_not_in_rejected_state_error(self):
        """Test _reset_to_draft raises UserError if not in 'rejected' state."""
        self.change_request.state = "pending"
        with self.assertRaises(UserError) as e:
            self.test_cr_type_record._reset_to_draft(self.change_request)
        self.assertEqual(
            str(e.exception), "The request to be cancelled must be in draft, pending, or rejected validation state."
        )
