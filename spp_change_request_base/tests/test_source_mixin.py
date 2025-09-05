from unittest.mock import patch

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestChangeRequestSourceMixin(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user_admin = cls.env.ref("base.group_system")
        cls.user_demo = cls.env["res.users"].create(
            {
                "name": "Test User",
                "login": "test_user",
            }
        )
        cls.user_demo.groups_id = [(4, cls.user_admin.id)]

        # Patch to allow creating spp.change.request
        patcher = patch(
            "odoo.addons.spp_change_request_base.models.change_request.ChangeRequestBase._selection_request_type_ref_id"
        )
        mock_selection = patcher.start()
        mock_selection.return_value = [("test.cr.type", "Test CR Type")]
        mock_selection.__name__ = "_mocked__selection_request_type_ref_id"
        cls.addClassCleanup(patcher.stop)

        patcher = patch(
            "odoo.addons.spp_change_request_base.models.change_request.ChangeRequestValidationSequence._selection_request_type_ref_id"
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
        stage_local = self.env["spp.change.request.validation.stage"].create(
            {
                "name": "Local Stage",
            }
        )
        stage_global = self.env["spp.change.request.validation.stage"].create(
            {
                "name": "Global Stage",
            }
        )
        validations_local = self.env["spp.change.request.validation.sequence"].create(
            {
                "sequence": 10,
                "stage_id": stage_local.id,
                "request_type": "test.cr.type",
                "validation_group_id": self.env.ref("base.user_admin").id,
                "validation_group_state": "both",
            }
        )
        validations_global = self.env["spp.change.request.validation.sequence"].create(
            {
                "sequence": 20,
                "stage_id": stage_global.id,
                "request_type": "test.cr.type",
                "validation_group_id": self.env.ref("base.user_admin").id,
                "validation_group_state": "both",
            }
        )
        self.test_cr_type_record.validation_ids = [(4, validations_local.id), (4, validations_global.id)]

    def test_01_update_registrant_id(self):
        """Test that registrant_id is updated based on request_type_ref_id."""
        # Initially, registrant_id should be empty
        self.assertFalse(self.change_request.registrant_id)

        # Set a registrant and request_type_ref_id
        partner = self.env["res.partner"].create({"name": "Test Partner"})
        self.test_cr_type_record.registrant_id = partner.id
        self.change_request.request_type_ref_id = self.test_cr_type_record
        # Simulate onchange
        self.test_cr_type_record._update_registrant_id(self.test_cr_type_record)

        # Now, registrant_id should be cleared
        self.assertEqual(self.change_request.registrant_id, partner)

    def test_02_on_submit_draft_state(self):
        """Test _on_submit when the request is in 'draft' state."""
        dms_directory = self.env["spp.dms.directory"].create({"name": "Test Directory"})
        self.change_request.dms_directory_ids = [(4, dms_directory.id)]
        self.assertEqual(self.change_request.state, "draft")
        self.test_cr_type_record.action_submit()
        self.assertEqual(self.change_request.state, "pending")
        self.assertIsNotNone(self.change_request.date_requested)

    def test_03_on_submit_not_draft_state_error(self):
        """Test _on_submit raises ValidationError if not in 'draft' state."""
        self.change_request.state = "pending"
        with self.assertRaises(ValidationError) as e:
            self.test_cr_type_record._on_submit(self.change_request)
        self.assertEqual(str(e.exception), "The request must be in draft state to be set to pending validation.")

    def test_04_apply_not_validated_state_error(self):
        """Test _apply raises ValidationError if not in 'validated' state."""
        self.change_request.state = "pending"
        with self.assertRaises(ValidationError) as e:
            self.test_cr_type_record._apply(self.change_request)
        self.assertEqual(str(e.exception), "The request must be in validated state for changes to be applied.")

    def test_05_apply_success(self):
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

    def test_06_cancel_in_valid_state(self):
        """Test _cancel when request is in a cancellable state."""
        self.change_request.state = "pending"
        self.test_cr_type_record._cancel(self.change_request)
        self.assertEqual(self.change_request.state, "cancelled")
        self.assertEqual(self.change_request.cancelled_by_id, self.env.user)
        self.assertIsNotNone(self.change_request.date_cancelled)

    def test_07_cancel_in_invalid_state_error(self):
        """Test _cancel raises UserError if in a non-cancellable state."""
        self.change_request.state = "applied"
        with self.assertRaises(UserError) as e:
            self.test_cr_type_record._cancel(self.change_request)
        self.assertEqual(
            str(e.exception), "The request to be cancelled must be in draft, pending, or rejected validation state."
        )

    def test_08_reset_to_draft_in_rejected_state(self):
        """Test _reset_to_draft when request is in 'rejected' state."""
        self.change_request.state = "rejected"
        self.test_cr_type_record._reset_to_draft(self.change_request)
        self.assertEqual(self.change_request.state, "draft")
        self.assertEqual(self.change_request.reset_to_draft_by_id, self.env.user)

    def test_09_reset_to_draft_not_in_rejected_state_error(self):
        """Test _reset_to_draft raises UserError if not in 'rejected' state."""
        self.change_request.state = "pending"
        with self.assertRaises(UserError) as e:
            self.test_cr_type_record._reset_to_draft(self.change_request)
        self.assertEqual(
            str(e.exception), "The request to be cancelled must be in draft, pending, or rejected validation state."
        )

    def test_10_on_validate(self):
        """Test _on_validate success path."""
        self.change_request.assign_to_id = self.user_demo.id
        self.change_request.request_type_ref_id = self.test_cr_type_record
        self.test_cr_type_record.action_submit()
        self.test_cr_type_record.with_user(self.user_demo).action_validate()
        # Second Call for Global Stage Validation
        self.test_cr_type_record.with_user(self.user_demo).action_validate()
        self.assertEqual(self.change_request.state, "applied")
        self.assertIsNotNone(self.change_request.date_validated)

    def test_11_approve_cr_directly(self):
        """Test approving a CR directly without validations."""
        self.change_request.request_type_ref_id = self.test_cr_type_record
        self.test_cr_type_record._approve_cr(self.change_request)
        self.assertEqual(self.change_request.state, "applied")

    def test_12_call_action_cancel(self):
        """Test action_cancel method."""
        self.change_request.state = "pending"
        action = self.test_cr_type_record.action_cancel()
        self.assertEqual(action["res_model"], "spp.change.request.cancel.wizard")

    def test_13_call_action_reject(self):
        """Test action_reject method."""
        self.change_request.state = "pending"
        action = self.test_cr_type_record.action_reject()
        self.assertEqual(action["res_model"], "spp.change.request.reject.wizard")

    def test_14_on_reject(self):
        """Test _on_reject method."""
        self.change_request.state = "pending"
        self.test_cr_type_record._on_reject(self.change_request, "Rejection Reason")
        self.assertEqual(self.change_request.state, "rejected")

    @patch(
        "odoo.addons.spp_change_request_base.models.mixins.source_mixin.ChangeRequestSourceMixin.ADMIN_GROUP_NAME",
        "base.group_system",
    )
    def test_15_call_open_user_assignment_wiz(self):
        """Test open_user_assignment_wiz method."""
        self.change_request.assign_to_id = False
        action = self.test_cr_type_record.with_user(self.user_demo).open_user_assignment_wiz()
        # First without assigned user
        self.assertEqual(self.change_request.assign_to_id, self.user_demo)

        action = self.test_cr_type_record.with_user(self.user_demo).open_user_assignment_wiz()

        self.assertEqual(action["res_model"], "spp.change.request.user.assign.wizard")

    def test_16_call_open_user_assignment_to_wiz(self):
        """Test open_user_assignment_to_wiz method."""
        action = self.test_cr_type_record.with_user(self.user_demo).open_user_assignment_to_wiz()
        self.assertEqual(action["res_model"], "spp.change.request.user.assign.wizard")

    @patch(
        "odoo.addons.spp_change_request_base.models.mixins.source_mixin.ChangeRequestSourceMixin.REGISTRANT_FORM_ID",
        "base.view_partner_form",
    )
    def test_17_call_open_registrant_details_form(self):
        """Test open_user_assignment_wiz method."""
        action = self.test_cr_type_record.with_user(self.user_demo).open_registrant_details_form()

        self.assertEqual(action["res_model"], "res.partner")
