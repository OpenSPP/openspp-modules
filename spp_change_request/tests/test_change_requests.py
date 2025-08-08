import logging
from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
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
        cls.individual_1 = cls.env["res.partner"].create(
            {
                "name": "Test Individual 1",
                "is_registrant": True,
                "is_group": False,
                "phone": "+1234567890",
            }
        )
        cls.individual_2 = cls.env["res.partner"].create(
            {
                "name": "Test Individual 2",
                "is_registrant": True,
                "is_group": False,
                "phone": "+0987654321",
            }
        )
        cls.group = cls.env["res.partner"].create(
            {
                "name": "Test Group",
                "is_registrant": True,
                "is_group": True,
            }
        )

        # Add individuals to group
        cls.env["g2p.group.membership"].create(
            {
                "group": cls.group.id,
                "individual": cls.individual_1.id,
            }
        )
        cls.env["g2p.group.membership"].create(
            {
                "group": cls.group.id,
                "individual": cls.individual_2.id,
            }
        )

    @patch("odoo.addons.spp_change_request.models.change_request.ChangeRequestBase._selection_request_type_ref_id")
    def _create_test_change_request(self, mock_request_type_selection, **kwargs):
        """Helper method to create a test change request"""
        mock_request_type_selection.return_value = [("test.request.type", "Test Request Type")]
        mock_request_type_selection.__name__ = "_mocked__selection_request_type_ref_id"

        default_vals = {
            "name": "Test Request",
            "request_type": "test.request.type",
            "registrant_id": self.individual_1.id,
            "applicant_id": self.individual_1.id,
            "applicant_phone": "+1234567890",
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

    def test_07_compute_fields(self):
        """Test computed fields"""
        change_request = self._create_test_change_request()

        # Test registrant_id_visible
        self.assertTrue(change_request.registrant_id_visible)

        # Test applicant_id_required
        self.assertTrue(change_request.applicant_id_required)

        # Test applicant_id_visible
        self.assertTrue(change_request.applicant_id_visible)

        # Test applicant_phone_required
        self.assertTrue(change_request.applicant_phone_required)

        # Test applicant_information_visible
        self.assertTrue(change_request.applicant_information_visible)

    def test_08_compute_domains(self):
        """Test computed domains"""
        change_request = self._create_test_change_request()

        # Test registrant_id_domain
        change_request._compute_registrant_id_domain()
        self.assertIsInstance(change_request.registrant_id_domain, list)

        # Test applicant_id_domain
        self.assertEqual(change_request.applicant_id_domain, [("is_registrant", "=", True), ("is_group", "=", False)])

    def test_09_onchange_methods(self):
        """Test onchange methods"""
        change_request = self._create_test_change_request()

        # Test onchange_registrant_id
        change_request.registrant_id = self.group
        change_request._onchange_registrant_id()
        self.assertFalse(change_request.applicant_id)

        # Test onchange_applicant_id
        change_request.applicant_id = self.individual_2
        change_request._onchange_applicant_id()
        self.assertEqual(change_request.applicant_phone, self.individual_2.phone)

    def test_10_phone_validation(self):
        """Test phone validation"""
        change_request = self._create_test_change_request()

        # Test with valid phone
        change_request.applicant_phone = "+1234567890"
        change_request._check_applicant_phone()  # Should not raise error

    def test_11_scan_id_document(self):
        """Test ID document scanning"""
        change_request = self._create_test_change_request()

        # Test with empty details
        change_request.id_document_details = ""
        change_request._onchange_scan_id_document_details()  # Should not raise error

    def test_12_scan_qr_code(self):
        """Test QR code scanning"""
        change_request = self._create_test_change_request()

        # Test with empty details
        change_request.qr_code_details = ""
        change_request._onchange_scan_qr_code_details()  # Should not raise error

        # Test with invalid QR code
        change_request.qr_code_details = '{"qrcode": "invalid-code"}'
        with self.assertRaises(UserError):
            change_request._onchange_scan_qr_code_details()

    def test_13_open_forms(self):
        """Test opening forms"""
        change_request = self._create_test_change_request()

        # Test open_change_request_form
        result = change_request.open_change_request_form()
        self.assertIsInstance(result, dict)

        # Test open_applicant_form
        result = change_request.open_applicant_form()
        self.assertIsInstance(result, dict)

        # Test open_user_assignment_wiz
        result = change_request.open_user_assignment_wiz()
        self.assertIsInstance(result, dict)

    def test_14_open_request_detail(self):
        """Test opening request detail"""
        change_request = self._create_test_change_request()

        # Test with phone
        change_request.applicant_phone = "+1234567890"
        result = change_request.open_request_detail()
        self.assertIsInstance(result, dict)

    def test_23_check_user(self):
        """Test user permission check"""
        change_request = self._create_test_change_request()

        # Test with assigned user
        self.assertTrue(change_request._check_user("Apply"))

        # Test without assigned user
        change_request.assign_to_id = False
        with self.assertRaises(UserError):
            change_request._check_user("Apply")

    def test_24_check_user_wrong_user(self):
        """Test user permission check with wrong user"""
        change_request = self._create_test_change_request()

        with self.assertRaises(UserError):
            change_request.with_user(self.user_demo)._check_user("Apply")

    def test_25_compute_validation_group_id(self):
        """Test validation group ID computation"""
        change_request = self._create_test_change_request()

        change_request._compute_validation_group_id()
        # Should compute based on validator_ids and state


@tagged("post_install", "-at_install")
class TestChangeRequestValidators(TransactionCase):
    @classmethod
    @patch("odoo.addons.spp_change_request.models.change_request.ChangeRequestBase._selection_request_type_ref_id")
    def setUpClass(cls, mock_request_type_selection):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )

        # Mock the request type selection
        mock_request_type_selection.return_value = [("test.request.type", "Test Request Type")]
        mock_request_type_selection.__name__ = "_mocked__selection_request_type_ref_id"

        # Create test data
        cls.user = cls.env.ref("base.user_admin")
        cls.stage = cls.env["spp.change.request.validation.stage"].create(
            {
                "name": "Test Stage",
            }
        )
        cls.change_request = cls.env["spp.change.request"].create(
            {
                "name": "Test Request",
                "request_type": "test.request.type",
            }
        )

    def test_01_validator_creation(self):
        """Test validator creation"""
        validator = self.env["spp.change.request.validators"].create(
            {
                "request_id": self.change_request.id,
                "stage_id": self.stage.id,
                "validator_id": self.user.id,
            }
        )

        self.assertEqual(validator.request_id, self.change_request)
        self.assertEqual(validator.stage_id, self.stage)
        self.assertEqual(validator.validator_id, self.user)

    def test_02_validator_date_validation(self):
        """Test validator date validation"""
        validator = self.env["spp.change.request.validators"].create(
            {
                "request_id": self.change_request.id,
                "stage_id": self.stage.id,
                "validator_id": self.user.id,
            }
        )

        # Test that date_validated is set
        self.assertIsNotNone(validator.date_validated)


@tagged("post_install", "-at_install")
class TestChangeRequestTargets(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )

    def test_01_target_creation(self):
        """Test target creation"""
        target = self.env["spp.change.request.targets"].create(
            {
                "name": "Test Target",
                "target": "individual",
            }
        )

        self.assertEqual(target.name, "Test Target")
        self.assertEqual(target.target, "individual")

    def test_02_target_selection_values(self):
        """Test target selection values"""
        target_individual = self.env["spp.change.request.targets"].create(
            {
                "name": "Individual Target",
                "target": "individual",
            }
        )
        target_group = self.env["spp.change.request.targets"].create(
            {
                "name": "Group Target",
                "target": "group",
            }
        )
        target_both = self.env["spp.change.request.targets"].create(
            {
                "name": "Both Target",
                "target": "both",
            }
        )

        self.assertEqual(target_individual.target, "individual")
        self.assertEqual(target_group.target, "group")
        self.assertEqual(target_both.target, "both")


@tagged("post_install", "-at_install")
class TestChangeRequestStage(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )

    def test_01_stage_creation(self):
        """Test stage creation"""
        stage = self.env["spp.change.request.validation.stage"].create(
            {
                "name": "Test Stage",
            }
        )

        self.assertEqual(stage.name, "Test Stage")

    def test_02_stage_ordering(self):
        """Test stage ordering"""
        stage_1 = self.env["spp.change.request.validation.stage"].create(
            {
                "name": "Stage 1",
            }
        )
        stage_2 = self.env["spp.change.request.validation.stage"].create(
            {
                "name": "Stage 2",
            }
        )

        stages = self.env["spp.change.request.validation.stage"].search([])
        self.assertIn(stage_1, stages)
        self.assertIn(stage_2, stages)
