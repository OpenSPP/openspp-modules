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

    def _create_change_request(self):
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

    # def test_04_validate_data(self):
    #     self.assertEqual(1, 1)

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

    # def test_06_action_validate(self):

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
        pass
