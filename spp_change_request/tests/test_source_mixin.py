from unittest.mock import patch

from odoo.exceptions import UserError, ValidationError

from .common import Common


class ChangeRequestSourceMixinTest(Common):
    @patch(
        "odoo.addons.spp_change_request.models.change_request.ChangeRequestBase._selection_request_type_ref_id"
    )
    def setUp(self, mock_request_type_selection):
        super().setUp()
        mock_request_type_selection.__name__ = "_mocked___selection_request_type_ref_id"

        mock_request_type_selection.return_value = [
            ("source.mixin.test.model", "Test Request Type")
        ]

        self._test_change_request = self._create_change_request()
        self._test_change_request.applicant_phone = "+639277817283"
        self._test_change_request.registrant_id = self._test_group
        self._test_change_request.applicant_id = self._test_individual_1
        self._test_change_request.with_context(
            unittest=True
        ).create_request_detail_no_redirect()
        self.test_request_type = self._test_change_request.request_type_ref_id
        self.test_user = self.env["res.users"].create({"name": "test", "login": "test"})

    @patch(
        "odoo.addons.spp_change_request.models.change_request.ChangeRequestBase._selection_request_type_ref_id"
    )
    def _create_change_request(self, mock_request_type_selection):
        mock_request_type_selection.__name__ = "_mocked___selection_request_type_ref_id"

        mock_request_type_selection.return_value = [
            ("source.mixin.test.model", "Test Request Type")
        ]
        return self.env["spp.change.request"].create(
            {
                "name": "Test Request",
                "request_type": "source.mixin.test.model",
            }
        )

    def test_01_update_registrant_id(self):
        self.test_request_type.registrant_id = self._test_individual_2
        self.test_request_type._update_registrant_id([self.test_request_type])

        self.assertEqual(
            self._test_change_request.registrant_id, self._test_individual_2
        )

    def test_02_get_request_type_view_id(self):
        self.assertIsNotNone(self.test_request_type.get_request_type_view_id())

    def test_03_update_live_data(self):
        with self.assertRaises(NotImplementedError):
            self.test_request_type.update_live_data()

    def test_04_validate_data(self):
        with self.assertRaises(ValidationError):
            self.test_request_type.validate_data()

    @patch(
        "odoo.addons.spp_change_request.models.mixins.source_mixin.ChangeRequestSourceMixin.check_required_documents",
        return_value=True,
    )
    def test_05_action_submit(self, mocker):
        mocker.__name__ = "_mocked__check_required_documents"
        self._test_change_request.state = "pending"
        with self.assertRaisesRegex(
            UserError,
            "The request must be in draft state to be set to pending validation.",
        ):
            self.test_request_type.action_submit()

        self._test_change_request.state = "draft"
        self.test_request_type.action_submit()
        self.assertEqual(self._test_change_request.state, "pending")

        self._test_change_request.state = "draft"
        self._test_change_request.action_submit()
        self.assertEqual(self._test_change_request.state, "pending")

    def test_06_action_validate(self):
        self._test_change_request.state = "draft"
        with self.assertRaisesRegex(
            ValidationError,
            "The request to be validated must be in submitted state.",
        ):
            self.test_request_type.action_validate()

        self._test_change_request.state = "pending"

        with self.assertRaisesRegex(
            ValidationError,
            "There are no validators defined for this request.",
        ):
            self.test_request_type.action_validate()

    def test_07_auto_apply_conditions(self):
        self.assertTrue(self.test_request_type.auto_apply_conditions())

    @patch(
        "odoo.addons.spp_change_request.models.mixins.source_mixin.ChangeRequestSourceMixin.update_live_data",
        return_value=True,
    )
    def test_08_action_apply(self, mocker):
        mocker.__name__ = "_mocked__update_live_data"
        with self.assertRaisesRegex(
            ValidationError,
            "The request must be in validated state for changes to be applied.",
        ):
            self.test_request_type.action_apply()

        self._test_change_request.state = "validated"
        self.test_request_type.action_apply()
        self.assertEqual(self.test_request_type.state, "applied")

    def test_09_action_cancel(self):
        action = self.test_request_type.action_cancel()

        self.assertEqual(action.get("name"), "Cancel Change Request")

    def test_10_cancel(self):
        self._test_change_request.state = "applied"
        with self.assertRaisesRegex(
            UserError,
            "The request to be cancelled must be in draft, pending, or rejected validation state.",
        ):
            self.test_request_type._cancel(self.test_request_type.change_request_id)

        self._test_change_request.state = "draft"
        self.test_request_type._cancel(self.test_request_type.change_request_id)
        self.assertEqual(self.test_request_type.state, "cancelled")

    def test_11_action_reset_to_draft(self):
        self._test_change_request.state = "draft"

        with self.assertRaisesRegex(
            UserError,
            "The request to be cancelled must be in draft, pending, or rejected validation state.",
        ):
            self.test_request_type.action_reset_to_draft()

        self._test_change_request.state = "rejected"
        self.test_request_type.action_reset_to_draft()

        self.assertEqual(self.test_request_type.state, "draft")

    def test_12_action_reject(self):
        action = self.test_request_type.action_reject()

        self.assertEqual(
            [action.get("name"), action.get("type"), action.get("view_mode")],
            ["Reject Change Request", "ir.actions.act_window", "form"],
        )

    def test_13_on_reject(self):
        rejected_remarks = "test rejected remarks"

        self._test_change_request.state = "cancelled"
        with self.assertRaisesRegex(
            UserError,
            "The request to be rejected must be in draft or pending validation state.",
        ):
            self.test_request_type._on_reject(
                self.test_request_type.change_request_id, rejected_remarks
            )

        self._test_change_request.state = "draft"

        self.test_request_type._on_reject(
            self.test_request_type.change_request_id, rejected_remarks
        )
        self.assertEqual(self.test_request_type.state, "rejected")

    def test_14_copy_group_member_ids_condition(self):
        self.assertTrue(self.test_request_type.copy_group_member_ids_condition())

    def test_15_open_applicant_details_form(self):
        action = self.test_request_type.open_applicant_details_form()

        self.assertEqual(
            [action.get("name"), action.get("target")], ["Applicant Details", "new"]
        )

    def test_16_open_user_assignment_wiz(self):
        self._test_change_request.assign_to_id = self.env.user

        action = self.test_request_type.open_user_assignment_wiz()
        self.assertEqual(
            [action.get("name"), action.get("type"), action.get("view_mode")],
            ["Assign Change Request to User", "ir.actions.act_window", "form"],
        )

        self._test_change_request.assign_to_id = False
        self.test_request_type.open_user_assignment_wiz()
        self.assertEqual(self.test_request_type.assign_to_id, self.env.user)

        self._test_change_request.assign_to_id = self.test_user.id
        self.test_request_type.open_user_assignment_wiz()
        self.assertEqual(self.test_request_type.assign_to_id, self.env.user)

    def test_17_open_user_assignment_to_wiz(self):
        action = self.test_request_type.open_user_assignment_to_wiz()
        self.assertEqual(
            [action.get("name"), action.get("type"), action.get("view_mode")],
            ["Assign Change Request to User", "ir.actions.act_window", "form"],
        )

    def test_18_compute_current_user_assigned(self):
        self.test_request_type.with_context(
            uid=self.env.user.id
        )._compute_current_user_assigned()

        self.assertTrue(self.test_request_type.current_user_assigned)

    def test_19_check_required_documents(self):
        addtional_request_docs = ["spp_change_request.pds_dms_extra_documents"]

        with self.assertRaises(ValidationError):
            self.test_request_type.check_required_documents(addtional_request_docs)

        with self.assertRaises(ValidationError):
            self.test_request_type.check_required_documents()

    def test_20_action_attach_documents(self):
        with self.assertRaisesRegex(
            UserError, "The required document category is not configured."
        ):
            self.test_request_type.with_context(
                category_id=9999999
            ).action_attach_documents()

        action = self.test_request_type.with_context(
            category_id=self.env.ref("spp_change_request.pds_dms_extra_documents").id
        ).action_attach_documents()
        self.assertEqual(
            [action.get("type"), action.get("view_mode"), action.get("res_model")],
            ["ir.actions.act_window", "form", "dms.file"],
        )

    def test_21_open_registrant_details_form(self):
        action = self.test_request_type.open_registrant_details_form()

        self.assertEqual(
            [action.get("name"), action.get("target")], ["Group Details", "new"]
        )

    def test_22_show_notification(self):
        title = "title"
        message = "test message"
        kind = "test kind"
        action = self.test_request_type.show_notification(title, message, kind)

        self.assertEqual(
            [
                action["params"]["message"],
                action["params"]["type"],
                action.get("type"),
                action.get("tag"),
            ],
            [message, kind, "ir.actions.client", "display_notification"],
        )

    def test_23_unlink(self):
        self._test_change_request.unlink()

    def test_24_open_request_detail(self):
        res = self._test_change_request.with_context(
            show_validation_form=True
        ).open_request_detail()
        self.assertIsNotNone(res)

    def test_25_get_validation_stage(self):
        stage, message, validator_id = self._test_change_request._get_validation_stage()
        self.assertEqual(
            [stage, message, validator_id],
            [
                None,
                "There are no validators defined for this request.",
                self.env.user.id,
            ],
        )

    def test_26_cancel_wizard(self):
        self._test_change_request_2 = self._create_change_request()
        self._test_change_request_2.applicant_phone = "+639277817283"
        self._test_change_request_2.registrant_id = self._test_group
        self._test_change_request_2.applicant_id = self._test_individual_1

        self.wizard_1 = (
            self.env["spp.change.request.cancel.wizard"]
            .with_context(change_request_id=self._test_change_request.id)
            .create({})
        )
        self.wizard_2 = (
            self.env["spp.change.request.cancel.wizard"]
            .with_context(active_id=self._test_change_request_2.id)
            .create({})
        )

        self.assertIsNotNone(self.wizard_1)
        self.assertIsNotNone(self.wizard_2)

        self.wizard_1.cancel_change_request()
        self.assertEqual(self._test_change_request.state, "cancelled")

        self.wizard_2.cancel_change_request()
        self.assertEqual(self._test_change_request.state, "cancelled")

        self.wizard_1._compute_message()
        self.assertEqual(
            self.wizard_1.dialog_message,
            f"Are you sure you would like to cancel this request: {self._test_change_request.name}",
        )

    def test_27_confirm_user_wizard(self):
        self.wizard_1 = (
            self.env["spp.change.request.user.assign.wizard"]
            .with_context(
                change_request_id=self._test_change_request.id,
                curr_assign_to_id=self.test_user.id,
                assign_to=True,
            )
            .create({})
        )

        self.wizard_2 = (
            self.env["spp.change.request.user.assign.wizard"]
            .with_context(active_id=self._test_change_request.id)
            .create({})
        )

        self.assertIsNotNone(self.wizard_1)
        self.assertIsNotNone(self.wizard_2)

        self.wizard_1.assign_to_user()
        self.assertEqual(
            self.wizard_1.change_request_id.assign_to_id.id, self.env.user.id
        )

        self.wizard_1._compute_message_assignment()
        self.assertEqual(
            [self.wizard_1.dialog_message, self.wizard_1.assign_to_any],
            ["Assign this change request to:", True],
        )

        self.wizard_1._compute_assign_to_id_domain()
        self.assertIsNotNone(self.wizard_1.assign_to_id_domain)

    def test_28_reject_wizard(self):
        self.wizard_1 = (
            self.env["spp.change.request.reject.wizard"]
            .with_context(change_request_id=self._test_change_request.id)
            .create({"rejected_remarks": "Rejected"})
        )
        self.assertIsNotNone(self.wizard_1)

        self.wizard_1.reject_change_request()
        self.assertEqual(self.wizard_1.change_request_id.state, "rejected")

        self.wizard_1._compute_message()
        self.assertEqual(
            self.wizard_1.dialog_message,
            f"Are you sure you would like to reject this request: {self.wizard_1.change_request_id.name}",
        )
