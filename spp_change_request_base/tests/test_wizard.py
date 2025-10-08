import json
import logging
from unittest.mock import patch

from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestWizards(TransactionCase):
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
        cls.user_admin = cls.env.ref("base.group_system")
        cls.user_demo = cls.env["res.users"].create(
            {
                "name": "Test User",
                "login": "test_user",
                "password": "test_password",
            }
        )
        cls.user_demo.groups_id = [(4, cls.user_admin.id)]
        cls.user_demo2 = cls.env["res.users"].create(
            {
                "name": "Test User2",
                "login": "test_user2",
                "password": "test_password2",
            }
        )
        # Create test registrants
        cls.registrant_1 = cls.env["res.partner"].create(
            {
                "name": "Test Partner 2",
                "phone": "+0987654321",
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

    def _create_test_cr(self):
        default_vals = {
            "name": "Test Request",
            "request_type": "test.cr.type",
            "registrant_id": self.registrant_1.id,
        }

        return self.env["spp.change.request"].create(default_vals)

    def test_01_cancel_wizard_with_cr_type(self):
        """Test cancel_change_request_wizard functionality."""
        change_request = self._create_test_cr()
        self.env["test.cr.type"].create(
            {
                "change_request_id": change_request.id,
            }
        )
        wizard = self.env["spp.change.request.cancel.wizard"].create(
            {
                "change_request_id": change_request.id,
            }
        )
        wizard.cancel_change_request()
        self.assertEqual(change_request.state, "cancelled")

    def test_02_cancel_wizard_without_cr_type(self):
        """Test cancel_change_request_wizard functionality."""
        change_request = self._create_test_cr()
        wizard = self.env["spp.change.request.cancel.wizard"].create(
            {
                "change_request_id": change_request.id,
            }
        )
        wizard.cancel_change_request()
        self.assertEqual(change_request.state, "cancelled")

    def test_03_cancel_wizard_compute_message(self):
        """Test _compute_message functionality."""
        change_request = self._create_test_cr()
        wizard = self.env["spp.change.request.cancel.wizard"].create(
            {
                "change_request_id": change_request.id,
            }
        )
        wizard._compute_message()
        expected_message = "Are you sure you would like to cancel this request: %s" % change_request.name
        self.assertEqual(wizard.dialog_message, expected_message)

    def test_04_reject_wizard_compute_message(self):
        """Test _compute_message for reject wizard."""
        change_request = self._create_test_cr()
        wizard = self.env["spp.change.request.reject.wizard"].create(
            {
                "change_request_id": change_request.id,
                "rejected_remarks": "Test rejection",
            }
        )
        wizard._compute_message()
        expected_message = "Are you sure you would like to reject this request: %s" % change_request.name
        self.assertEqual(wizard.dialog_message, expected_message)

    def test_05_reject_wizard_reject_change_request(self):
        """Test reject_change_request for reject wizard."""
        change_request = self._create_test_cr()
        cr_type = self.env["test.cr.type"].create(
            {
                "change_request_id": change_request.id,
            }
        )
        change_request.request_type_ref_id = cr_type
        change_request.state = "pending"

        wizard = self.env["spp.change.request.reject.wizard"].create(
            {
                "change_request_id": change_request.id,
                "rejected_remarks": "Test rejection",
            }
        )

        with patch.object(type(cr_type), "_on_reject", autospec=True) as mock_on_reject:
            wizard.reject_change_request()
            mock_on_reject.assert_called_once_with(cr_type, change_request, "Test rejection")

    def test_06_assign_wizard_assign_to_user(self):
        """Test assign_to_user for user assignment wizard."""
        change_request = self._create_test_cr()
        wizard = self.env["spp.change.request.user.assign.wizard"].create(
            {
                "change_request_id": change_request.id,
                "assign_to_id": self.user_demo.id,
            }
        )
        wizard.assign_to_user()
        self.assertEqual(change_request.assign_to_id, self.user_demo)

    def test_07_assign_wizard_compute_message(self):
        """Test _compute_message_assignment for user assignment wizard."""
        change_request = self._create_test_cr()
        wizard = self.env["spp.change.request.user.assign.wizard"].create(
            {
                "change_request_id": change_request.id,
            }
        )
        wizard._compute_message_assignment()
        self.assertEqual(wizard.dialog_message, "Assign this change request to:")
        self.assertTrue(wizard.assign_to_any)

    def test_08_assign_wizard_compute_domain(self):
        """Test _compute_assign_to_id_domain for user assignment wizard."""
        change_request = self._create_test_cr()
        wizard = self.env["spp.change.request.user.assign.wizard"].create(
            {
                "change_request_id": change_request.id,
            }
        )

        group1 = self.env["res.groups"].create({"name": "Test Group 1"})
        group2 = self.env["res.groups"].create({"name": "Test Group 2"})
        self.user_demo.groups_id = [(4, group1.id)]

        with patch.object(
            type(wizard.with_user(self.user_demo)), "_get_group_ids", return_value=[group1.id, group2.id]
        ) as mock_get_groups:
            wizard.with_user(self.user_demo)._compute_assign_to_id_domain()
            mock_get_groups.assert_called_once()
            domain = json.loads(wizard.assign_to_id_domain)
            self.assertEqual(domain, [["groups_id", "in", [group1.id]]])

    def test_09_assign_wizard_default_get(self):
        """Test default_get for user assignment wizard."""
        change_request = self._create_test_cr()
        change_request.assign_to_id = self.user_demo

        wizard = (
            self.env["spp.change.request.user.assign.wizard"]
            .with_context(active_id=change_request.id, curr_assign_to_id=self.user_demo2.id)
            .with_user(self.user_demo)
            .default_get([])
        )

        self.assertEqual(wizard["change_request_id"], change_request.id)
        self.assertEqual(wizard["curr_assign_to_id"], self.user_demo2.id)
        self.assertEqual(wizard["assign_to_id"], self.user_demo)

    def test_10_cancel_wizard_default_get(self):
        """Test default_get for cancel change request wizard."""
        change_request = self._create_test_cr()

        wizard = (
            self.env["spp.change.request.cancel.wizard"]
            .with_context(active_id=change_request.id)
            .with_user(self.user_demo)
            .default_get([])
        )

        self.assertEqual(wizard["change_request_id"], change_request.id)

        wizard_change_request = (
            self.env["spp.change.request.cancel.wizard"]
            .with_context(change_request_id=change_request.id)
            .with_user(self.user_demo)
            .default_get([])
        )

        self.assertEqual(wizard_change_request["change_request_id"], change_request.id)

    def test_11_reject_wizard_default_get(self):
        """Test default_get for reject change request wizard."""
        change_request = self._create_test_cr()

        wizard = (
            self.env["spp.change.request.reject.wizard"]
            .with_context(active_id=change_request.id)
            .with_user(self.user_demo)
            .default_get([])
        )

        self.assertEqual(wizard["change_request_id"], change_request.id)

        wizard_change_request = (
            self.env["spp.change.request.reject.wizard"]
            .with_context(change_request_id=change_request.id)
            .with_user(self.user_demo)
            .default_get([])
        )

        self.assertEqual(wizard_change_request["change_request_id"], change_request.id)
