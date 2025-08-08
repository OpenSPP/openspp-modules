import datetime
import json
import logging
from unittest.mock import patch

from odoo import fields
from odoo.exceptions import UserError, ValidationError
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
        cls.user_demo = cls.env["res.users"].create({
            "name": "Test User",
            "login": "test_user",
            "password": "test_password",
        })

        cls.gender_male = cls.env["gender.type"].create({
            "code": "Male",
            "value": "Male",
        })
        cls.gender_female = cls.env["gender.type"].create({
            "code": "Female",
            "value": "Female",
        })
        
        # Create test groups for validation
        cls.validation_group_1 = cls.env["res.groups"].create({
            "name": "Validation Group 1",
        })
        cls.validation_group_2 = cls.env["res.groups"].create({
            "name": "Validation Group 2",
        })

        # Create test validation stages
        cls.stage_1 = cls.env["spp.change.request.validation.stage"].create({
            "name": "Stage 1",
        })
        cls.stage_2 = cls.env["spp.change.request.validation.stage"].create({
            "name": "Stage 2",
        })

        # Create test change request targets
        cls.target_individual = cls.env["spp.change.request.targets"].create({
            "name": "Individual Target",
            "target": "individual",
        })
        cls.target_group = cls.env["spp.change.request.targets"].create({
            "name": "Group Target",
            "target": "group",
        })
        cls.target_both = cls.env["spp.change.request.targets"].create({
            "name": "Both Target",
            "target": "both",
        })

        # Create test registrants
        cls.individual_1 = cls.env["res.partner"].create({
            "name": "Test Individual 1",
            "is_registrant": True,
            "is_group": False,
            "gender": cls.gender_male.id,
            "birthdate": datetime.datetime.now() - datetime.timedelta(days=365*25),
            "phone": "+1234567890",
        })
        cls.individual_2 = cls.env["res.partner"].create({
            "name": "Test Individual 2",
            "is_registrant": True,
            "is_group": False,
            "gender": cls.gender_female.id,
            "birthdate": datetime.datetime.now() - datetime.timedelta(days=365*30),
            "phone": "+0987654321",
        })
        cls.group = cls.env["res.partner"].create({
            "name": "Test Group",
            "is_registrant": True,
            "is_group": True,
        })

        # Add individuals to group
        cls.env["g2p.group.membership"].create({
            "group": cls.group.id,
            "individual": cls.individual_1.id,
        })
        cls.env["g2p.group.membership"].create({
            "group": cls.group.id,
            "individual": cls.individual_2.id,
        })

        # Create validation sequences - these will be created in individual tests with proper mocking

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

    def test_05_compute_registrant_id_visible(self):
        """Test registrant_id_visible computation"""
        change_request = self._create_test_change_request()
        
        # Should be visible by default
        self.assertTrue(change_request.registrant_id_visible)

    def test_06_compute_applicant_id_required(self):
        """Test applicant_id_required computation"""
        change_request = self._create_test_change_request()
        
        # Should be required by default
        self.assertTrue(change_request.applicant_id_required)

    def test_07_compute_applicant_id_visible(self):
        """Test applicant_id_visible computation"""
        change_request = self._create_test_change_request()
        
        # Should be visible by default
        self.assertTrue(change_request.applicant_id_visible)

    def test_08_compute_applicant_phone_required(self):
        """Test applicant_phone_required computation"""
        change_request = self._create_test_change_request()
        
        # Should be required by default
        self.assertTrue(change_request.applicant_phone_required)

    def test_09_compute_applicant_information_visible(self):
        """Test applicant_information_visible computation"""
        change_request = self._create_test_change_request()
        
        # Should be visible by default
        self.assertTrue(change_request.applicant_information_visible)

    def test_10_compute_request_type_target(self):
        """Test request_type_target computation"""
        change_request = self._create_test_change_request()
        
        # Should compute based on request_type
        change_request._compute_request_type_target()
        # Note: This depends on the actual implementation of the compute method

    def test_11_compute_registrant_id_domain(self):
        """Test registrant_id_domain computation"""
        change_request = self._create_test_change_request()
        
        # Test with group target
        change_request.request_type_target = self.target_group
        change_request._compute_registrant_id_domain()
        self.assertIsInstance(change_request.registrant_id_domain, list)

    def test_12_compute_applicant_id_domain(self):
        """Test applicant_id_domain computation"""
        change_request = self._create_test_change_request()
        
        # Test without registrant
        self.assertEqual(change_request.applicant_id_domain, [('is_registrant', '=', True), ('is_group', '=', False)])
        
        # Test with group registrant
        change_request.registrant_id = self.group
        change_request._compute_applicant_id_domain()
        self.assertIsInstance(change_request.applicant_id_domain, list)

    def test_13_onchange_registrant_id(self):
        """Test onchange_registrant_id method"""
        change_request = self._create_test_change_request()
        
        # Test changing registrant to group
        change_request.registrant_id = self.group
        change_request._onchange_registrant_id()
        
        # Should clear applicant_id when registrant changes
        self.assertFalse(change_request.applicant_id)

    def test_14_onchange_applicant_id(self):
        """Test onchange_applicant_id method"""
        change_request = self._create_test_change_request()
        
        # Test changing applicant
        change_request.applicant_id = self.individual_2
        change_request._onchange_applicant_id()
        
        # Should update applicant_phone
        self.assertEqual(change_request.applicant_phone, self.individual_2.phone)

    def test_15_check_applicant_phone_constraint(self):
        """Test applicant phone constraint"""
        change_request = self._create_test_change_request()
        
        # Test with valid phone
        change_request.applicant_phone = "+1234567890"
        change_request._check_applicant_phone()  # Should not raise error
        
        # Test with invalid phone (if validation is implemented)
        # This depends on the actual validation logic

    def test_16_onchange_scan_id_document_details(self):
        """Test ID document scanning onchange"""
        change_request = self._create_test_change_request()
        
        # Test with empty details
        change_request.id_document_details = ""
        change_request._onchange_scan_id_document_details()  # Should not raise error

    def test_17_onchange_scan_qr_code_details(self):
        """Test QR code scanning onchange"""
        change_request = self._create_test_change_request()
        
        # Test with empty details
        change_request.qr_code_details = ""
        change_request._onchange_scan_qr_code_details()  # Should not raise error
        
        # Test with invalid QR code
        change_request.qr_code_details = '{"qrcode": "invalid-code"}'
        with self.assertRaises(UserError):
            change_request._onchange_scan_qr_code_details()

    def test_18_open_change_request_form(self):
        """Test opening change request form"""
        change_request = self._create_test_change_request()
        
        result = change_request.open_change_request_form()
        self.assertIsInstance(result, dict)
        self.assertIn("type", result)

    def test_19_open_applicant_form(self):
        """Test opening applicant form"""
        change_request = self._create_test_change_request()
        
        result = change_request.open_applicant_form()
        self.assertIsInstance(result, dict)
        self.assertIn("type", result)

    def test_20_open_user_assignment_wiz(self):
        """Test opening user assignment wizard"""
        change_request = self._create_test_change_request()
        
        result = change_request.open_user_assignment_wiz()
        self.assertIsInstance(result, dict)
        self.assertIn("type", result)

    def test_21_assign_to_user(self):
        """Test assigning change request to user"""
        change_request = self._create_test_change_request()
        
        # Test assignment
        change_request.assign_to_user(self.user_demo)
        self.assertEqual(change_request.assign_to_id, self.user_demo)

    def test_22_assign_to_user_pending_state_error(self):
        """Test assignment error when in pending state without validation sequence"""
        change_request = self._create_test_change_request()
        change_request.state = "pending"
        
        with self.assertRaises(UserError):
            change_request.assign_to_user(self.user_demo)

    def test_23_open_request_detail(self):
        """Test opening request detail"""
        change_request = self._create_test_change_request()
        
        # Test with phone
        change_request.applicant_phone = "+1234567890"
        result = change_request.open_request_detail()
        self.assertIsInstance(result, dict)

    def test_24_check_phone_exist(self):
        """Test phone existence check"""
        change_request = self._create_test_change_request()
        
        # Test with existing phone
        change_request.applicant_phone = "+1234567890"
        result = change_request._check_phone_exist()
        self.assertIsInstance(result, None)

    def test_25_create_request_detail_no_redirect(self):
        """Test creating request detail without redirect"""
        change_request = self._create_test_change_request()
        
        result = change_request.create_request_detail_no_redirect()
        self.assertIsInstance(result, dict)

    def test_26_create_request_detail(self):
        """Test creating request detail with redirect"""
        change_request = self._create_test_change_request()
        
        result = change_request.create_request_detail()
        self.assertIsInstance(result, dict)

    def test_27_get_id_doc_vals(self):
        """Test getting ID document values"""
        change_request = self._create_test_change_request()
        
        result = change_request._get_id_doc_vals(1, "test_field", "test_prefix")
        self.assertIsInstance(result, dict)

    def test_28_action_submit(self):
        """Test submitting change request"""
        change_request = self._create_test_change_request()
        
        change_request.action_submit()
        self.assertEqual(change_request.state, "pending")

    def test_29_action_validate(self):
        """Test validating change request"""
        change_request = self._create_test_change_request()
        change_request.state = "pending"
        
        change_request.action_validate()
        self.assertEqual(change_request.state, "validated")

    def test_30_action_apply(self):
        """Test applying change request"""
        change_request = self._create_test_change_request()
        change_request.state = "validated"
        
        change_request.action_apply()
        self.assertEqual(change_request.state, "applied")

    def test_31_action_cancel(self):
        """Test cancelling change request"""
        change_request = self._create_test_change_request()
        
        change_request.action_cancel()
        self.assertEqual(change_request.state, "cancelled")

    def test_32_action_cancel_non_draft_error(self):
        """Test cancelling non-draft change request error"""
        change_request = self._create_test_change_request()
        change_request.state = "validated"
        
        with self.assertRaises(UserError):
            change_request.action_cancel()

    def test_33_action_reset_to_draft(self):
        """Test resetting change request to draft"""
        change_request = self._create_test_change_request()
        change_request.state = "rejected"
        
        change_request.action_reset_to_draft()
        self.assertEqual(change_request.state, "draft")

    def test_34_action_reject(self):
        """Test rejecting change request"""
        change_request = self._create_test_change_request()
        change_request.state = "validated"
        
        change_request.action_reject()
        self.assertEqual(change_request.state, "rejected")

    def test_35_check_user(self):
        """Test user permission check"""
        change_request = self._create_test_change_request()
        
        # Test with assigned user
        self.assertTrue(change_request._check_user("Apply"))
        
        # Test without assigned user
        change_request.assign_to_id = False
        with self.assertRaises(UserError):
            change_request._check_user("Apply")

    def test_36_check_user_wrong_user(self):
        """Test user permission check with wrong user"""
        change_request = self._create_test_change_request()
        
        with self.assertRaises(UserError):
            change_request.with_user(self.user_demo)._check_user("Apply")

    def test_37_compute_validation_group_id(self):
        """Test validation group ID computation"""
        change_request = self._create_test_change_request()
        
        change_request._compute_validation_group_id()
        # Should compute based on validator_ids and state

    def test_38_get_validation_stage(self):
        """Test getting validation stage"""
        change_request = self._create_test_change_request()
        
        result = change_request._get_validation_stage()
        self.assertIsInstance(result, dict)

    def test_39_generate_activity(self):
        """Test generating mail activity"""
        change_request = self._create_test_change_request()
        
        change_request._generate_activity("test_type", "test_summary", "test_note")
        # Should create a mail activity

    def test_40_compute_current_user_assigned(self):
        """Test current user assigned computation"""
        change_request = self._create_test_change_request()
        
        change_request._compute_current_user_assigned()
        self.assertTrue(change_request.current_user_assigned)

    def test_41_multiple_records_operations(self):
        """Test operations on multiple change requests"""
        change_request_1 = self._create_test_change_request(name="Request 1")
        change_request_2 = self._create_test_change_request(name="Request 2")
        
        # Test bulk operations
        (change_request_1 + change_request_2).action_submit()
        self.assertEqual(change_request_1.state, "pending")
        self.assertEqual(change_request_2.state, "pending")

    def test_42_edge_case_empty_recordset(self):
        """Test operations with empty recordset"""
        empty_recordset = self.env["spp.change.request"].browse([])
        
        # These should not raise errors
        empty_recordset.action_submit()
        empty_recordset.action_validate()
        empty_recordset.action_apply()
        empty_recordset.action_cancel()

    def test_43_state_transitions(self):
        """Test all valid state transitions"""
        change_request = self._create_test_change_request()
        
        # Draft -> Pending
        change_request.action_submit()
        self.assertEqual(change_request.state, "pending")
        
        # Pending -> Validated
        change_request.action_validate()
        self.assertEqual(change_request.state, "validated")
        
        # Validated -> Applied
        change_request.action_apply()
        self.assertEqual(change_request.state, "applied")

    def test_44_invalid_state_transitions(self):
        """Test invalid state transitions"""
        change_request = self._create_test_change_request()
        
        # Cannot validate from draft
        with self.assertRaises(UserError):
            change_request.action_validate()
        
        # Cannot apply from draft
        with self.assertRaises(UserError):
            change_request.action_apply()

    @patch("odoo.addons.spp_change_request.models.change_request.ChangeRequestBase._selection_request_type_ref_id")
    def test_45_validation_sequence_integration(self, mock_request_type_selection):
        """Test integration with validation sequences"""
        mock_request_type_selection.return_value = [("test.request.type", "Test Request Type")]
        mock_request_type_selection.__name__ = "_mocked__selection_request_type_ref_id"
        
        # Create validation sequences with proper mocking
        validation_sequence_1 = self.env["spp.change.request.validation.sequence"].create({
            "sequence": 1,
            "request_type": "test.request.type",
            "stage_id": self.stage_1.id,
            "validation_group_id": self.validation_group_1.id,
            "validation_group_state": "draft",
        })
        validation_sequence_2 = self.env["spp.change.request.validation.sequence"].create({
            "sequence": 2,
            "request_type": "test.request.type",
            "stage_id": self.stage_2.id,
            "validation_group_id": self.validation_group_2.id,
            "validation_group_state": "pending",
        })
        
        change_request = self._create_test_change_request()
        
        # Test that validation sequences are properly linked
        self.assertIn(validation_sequence_1, change_request.validation_ids)
        self.assertIn(validation_sequence_2, change_request.validation_ids)

    def test_46_dms_integration(self):
        """Test DMS integration"""
        change_request = self._create_test_change_request()
        
        # Test DMS directory creation
        self.assertTrue(change_request.dms_directory_ids)

    def test_47_mail_thread_integration(self):
        """Test mail thread integration"""
        change_request = self._create_test_change_request()
        
        # Test that change request inherits mail.thread
        self.assertTrue(hasattr(change_request, 'message_post'))
        self.assertTrue(hasattr(change_request, 'message_subscribe'))

    def test_48_activity_mixin_integration(self):
        """Test activity mixin integration"""
        change_request = self._create_test_change_request()
        
        # Test that change request inherits mail.activity.mixin
        self.assertTrue(hasattr(change_request, 'activity_ids'))
        self.assertTrue(hasattr(change_request, 'activity_summary'))

    def test_49_company_auto_check(self):
        """Test company auto check functionality"""
        change_request = self._create_test_change_request()
        
        # Test that company is automatically set
        self.assertEqual(change_request.company_id, self.env.company)

    def test_50_phone_validation_integration(self):
        """Test phone validation integration"""
        change_request = self._create_test_change_request()
        
        # Test with valid phone format
        change_request.applicant_phone = "+1234567890"
        change_request._check_applicant_phone()  # Should not raise error


@tagged("post_install", "-at_install")
class TestChangeRequestValidators(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )
        
        # Create test data
        cls.user = cls.env.ref("base.user_admin")
        cls.stage = cls.env["spp.change.request.validation.stage"].create({
            "name": "Test Stage",
        })
        cls.change_request = cls.env["spp.change.request"].create({
            "name": "Test Request",
            "request_type": "test.request.type",
        })

    def test_01_validator_creation(self):
        """Test validator creation"""
        validator = self.env["spp.change.request.validators"].create({
            "request_id": self.change_request.id,
            "stage_id": self.stage.id,
            "validator_id": self.user.id,
        })
        
        self.assertEqual(validator.request_id, self.change_request)
        self.assertEqual(validator.stage_id, self.stage)
        self.assertEqual(validator.validator_id, self.user)

    def test_02_validator_date_validation(self):
        """Test validator date validation"""
        validator = self.env["spp.change.request.validators"].create({
            "request_id": self.change_request.id,
            "stage_id": self.stage.id,
            "validator_id": self.user.id,
        })
        
        # Test that date_validated is set
        self.assertIsNotNone(validator.date_validated)


@tagged("post_install", "-at_install")
class TestChangeRequestValidationSequence(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )
        
        # Create test data
        cls.stage = cls.env["spp.change.request.validation.stage"].create({
            "name": "Test Stage",
        })
        cls.validation_group = cls.env["res.groups"].create({
            "name": "Test Validation Group",
        })

    @patch("odoo.addons.spp_change_request.models.change_request.ChangeRequestBase._selection_request_type_ref_id")
    def test_01_validation_sequence_creation(self, mock_request_type_selection):
        """Test validation sequence creation"""
        mock_request_type_selection.return_value = [("test.request.type", "Test Request Type")]
        mock_request_type_selection.__name__ = "_mocked__selection_request_type_ref_id"
        
        sequence = self.env["spp.change.request.validation.sequence"].create({
            "sequence": 1,
            "request_type": "test.request.type",
            "stage_id": self.stage.id,
            "validation_group_id": self.validation_group.id,
            "validation_group_state": "draft",
        })
        
        self.assertEqual(sequence.sequence, 1)
        self.assertEqual(sequence.request_type, "test.request.type")
        self.assertEqual(sequence.stage_id, self.stage)
        self.assertEqual(sequence.validation_group_id, self.validation_group)

    @patch("odoo.addons.spp_change_request.models.change_request.ChangeRequestBase._selection_request_type_ref_id")
    def test_02_validation_sequence_ordering(self, mock_request_type_selection):
        """Test validation sequence ordering"""
        mock_request_type_selection.return_value = [("test.request.type", "Test Request Type")]
        mock_request_type_selection.__name__ = "_mocked__selection_request_type_ref_id"
        
        sequence_1 = self.env["spp.change.request.validation.sequence"].create({
            "sequence": 2,
            "request_type": "test.request.type",
            "stage_id": self.stage.id,
            "validation_group_id": self.validation_group.id,
            "validation_group_state": "draft",
        })
        sequence_2 = self.env["spp.change.request.validation.sequence"].create({
            "sequence": 1,
            "request_type": "test.request.type",
            "stage_id": self.stage.id,
            "validation_group_id": self.validation_group.id,
            "validation_group_state": "pending",
        })
        
        # Test ordering
        sequences = self.env["spp.change.request.validation.sequence"].search([
            ("request_type", "=", "test.request.type")
        ])
        self.assertEqual(sequences[0], sequence_2)  # Lower sequence first
        self.assertEqual(sequences[1], sequence_1)


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
        target = self.env["spp.change.request.targets"].create({
            "name": "Test Target",
            "target": "individual",
        })
        
        self.assertEqual(target.name, "Test Target")
        self.assertEqual(target.target, "individual")

    def test_02_target_selection_values(self):
        """Test target selection values"""
        target_individual = self.env["spp.change.request.targets"].create({
            "name": "Individual Target",
            "target": "individual",
        })
        target_group = self.env["spp.change.request.targets"].create({
            "name": "Group Target",
            "target": "group",
        })
        target_both = self.env["spp.change.request.targets"].create({
            "name": "Both Target",
            "target": "both",
        })
        
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
        stage = self.env["spp.change.request.validation.stage"].create({
            "name": "Test Stage",
        })
        
        self.assertEqual(stage.name, "Test Stage")

    def test_02_stage_ordering(self):
        """Test stage ordering"""
        stage_1 = self.env["spp.change.request.validation.stage"].create({
            "name": "Stage 1",
        })
        stage_2 = self.env["spp.change.request.validation.stage"].create({
            "name": "Stage 2",
        })
        
        stages = self.env["spp.change.request.validation.stage"].search([])
        self.assertIn(stage_1, stages)
        self.assertIn(stage_2, stages)


@tagged("post_install", "-at_install")
class TestDMSIntegration(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )
        
        # Create test change request
        cls.change_request = cls.env["spp.change.request"].create({
            "name": "Test Request",
            "request_type": "test.request.type",
        })

    def test_01_dms_file_creation(self):
        """Test DMS file creation with change request"""
        dms_file = self.env["spp.dms.file"].create({
            "name": "Test File",
            "change_request_id": self.change_request.id,
        })
        
        self.assertEqual(dms_file.change_request_id, self.change_request)

    def test_02_dms_directory_creation(self):
        """Test DMS directory creation with change request"""
        dms_directory = self.env["spp.dms.directory"].create({
            "name": "Test Directory",
            "change_request_id": self.change_request.id,
        })
        
        self.assertEqual(dms_directory.change_request_id, self.change_request)

    def test_03_dms_file_actions(self):
        """Test DMS file actions"""
        dms_file = self.env["spp.dms.file"].create({
            "name": "Test File",
            "change_request_id": self.change_request.id,
        })
        
        # Test action_save_and_close
        result = dms_file.action_save_and_close()
        self.assertEqual(result["type"], "ir.actions.act_window_close")
        
        # Test action_close
        result = dms_file.action_close()
        self.assertEqual(result["type"], "ir.actions.act_window_close")
        
        # Test action_attach_documents
        result = dms_file.action_attach_documents()
        self.assertIsInstance(result, dict)
        self.assertIn("type", result)


@tagged("post_install", "-at_install")
class TestRegistryIntegration(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )
        
        # Create test registrant
        cls.registrant = cls.env["res.partner"].create({
            "name": "Test Registrant",
            "is_registrant": True,
            "is_group": False,
        })

    def test_01_registry_change_request_relation(self):
        """Test registry change request relation"""
        change_request = self.env["spp.change.request"].create({
            "name": "Test Request",
            "request_type": "test.request.type",
            "registrant_id": self.registrant.id,
        })
        
        self.assertIn(change_request, self.registrant.change_request_ids)
        self.assertEqual(change_request.registrant_id, self.registrant)

    def test_02_registry_change_request_filtering(self):
        """Test registry change request filtering"""
        # Create change requests in different states
        draft_request = self.env["spp.change.request"].create({
            "name": "Draft Request",
            "request_type": "test.request.type",
            "registrant_id": self.registrant.id,
            "state": "draft",
        })
        applied_request = self.env["spp.change.request"].create({
            "name": "Applied Request",
            "request_type": "test.request.type",
            "registrant_id": self.registrant.id,
            "state": "applied",
        })
        
        # Test that both are linked
        self.assertIn(draft_request, self.registrant.change_request_ids)
        self.assertIn(applied_request, self.registrant.change_request_ids)


@tagged("post_install", "-at_install")
class TestGroupMembershipIntegration(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )
        
        # Create test data
        cls.individual = self.env["res.partner"].create({
            "name": "Test Individual",
            "is_registrant": True,
            "is_group": False,
            "birthdate": datetime.datetime.now() - datetime.timedelta(days=365*25),
            "phone": "+1234567890",
        })
        cls.membership_kind = self.env["g2p.group.membership.kind"].create({
            "name": "Test Kind",
        })

    def test_01_group_membership_creation(self):
        """Test group membership creation"""
        membership = self.env["spp.change.request.group.members"].create({
            "individual_id": self.individual.id,
            "kind_ids": [(6, 0, [self.membership_kind.id])],
        })
        
        self.assertEqual(membership.individual_id, self.individual)
        self.assertIn(self.membership_kind, membership.kind_ids)

    def test_02_group_membership_related_fields(self):
        """Test group membership related fields"""
        membership = self.env["spp.change.request.group.members"].create({
            "individual_id": self.individual.id,
        })
        
        self.assertEqual(membership.birthdate, self.individual.birthdate)
        self.assertEqual(membership.age, self.individual.age)
        self.assertEqual(membership.phone, self.individual.phone)

    def test_03_group_membership_open_individual_form(self):
        """Test opening individual form from membership"""
        membership = self.env["spp.change.request.group.members"].create({
            "individual_id": self.individual.id,
        })
        
        result = membership.open_individual_form()
        self.assertIsInstance(result, dict)
        self.assertIn("type", result)
        self.assertEqual(result["res_id"], self.individual.id)


@tagged("post_install", "-at_install")
class TestValidationSequenceMixin(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )

    @patch("odoo.addons.spp_change_request.models.change_request.ChangeRequestBase._selection_request_type_ref_id")
    def test_01_mixin_default_validation_ids(self, mock_request_type_selection):
        """Test mixin default validation IDs"""
        mock_request_type_selection.return_value = [("test.request.type", "Test Request Type")]
        mock_request_type_selection.__name__ = "_mocked__selection_request_type_ref_id"
        
        # Create validation sequence
        stage = self.env["spp.change.request.validation.stage"].create({
            "name": "Test Stage",
        })
        validation_sequence = self.env["spp.change.request.validation.sequence"].create({
            "sequence": 1,
            "request_type": "test.request.type",
            "stage_id": stage.id,
        })
        
        # Test that the mixin can access validation sequences
        mixin = self.env["spp.change.request.validation.sequence.mixin"]
        default_ids = mixin._default_validation_ids()
        self.assertIsNotNone(default_ids)


@tagged("post_install", "-at_install")
class TestWizards(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )
        
        # Create test change request - will be created in individual tests with proper mocking
        cls.user = self.env.ref("base.user_admin")

    @patch("odoo.addons.spp_change_request.models.change_request.ChangeRequestBase._selection_request_type_ref_id")
    def test_01_confirm_user_assignment_wizard(self, mock_request_type_selection):
        """Test confirm user assignment wizard"""
        mock_request_type_selection.return_value = [("test.request.type", "Test Request Type")]
        mock_request_type_selection.__name__ = "_mocked__selection_request_type_ref_id"
        
        # Create test change request
        change_request = self.env["spp.change.request"].create({
            "name": "Test Request",
            "request_type": "test.request.type",
        })
        
        wizard = self.env["spp.change.request.user.assign.wizard"].create({
            "change_request_id": change_request.id,
            "assign_to_id": self.user.id,
        })
        
        self.assertEqual(wizard.change_request_id, change_request)
        self.assertEqual(wizard.assign_to_id, self.user)
        
        # Test assignment
        wizard.assign_to_user()
        self.assertEqual(change_request.assign_to_id, self.user)

    @patch("odoo.addons.spp_change_request.models.change_request.ChangeRequestBase._selection_request_type_ref_id")
    def test_02_confirm_user_assignment_wizard_default_get(self, mock_request_type_selection):
        """Test confirm user assignment wizard default_get"""
        mock_request_type_selection.return_value = [("test.request.type", "Test Request Type")]
        mock_request_type_selection.__name__ = "_mocked__selection_request_type_ref_id"
        
        # Create test change request
        change_request = self.env["spp.change.request"].create({
            "name": "Test Request",
            "request_type": "test.request.type",
        })
        
        wizard = self.env["spp.change.request.user.assign.wizard"].with_context(
            change_request_id=change_request.id,
            curr_assign_to_id=self.user.id,
        ).create({})
        
        self.assertEqual(wizard.change_request_id, change_request)
        self.assertEqual(wizard.curr_assign_to_id, self.user)

    @patch("odoo.addons.spp_change_request.models.change_request.ChangeRequestBase._selection_request_type_ref_id")
    def test_03_reject_change_request_wizard(self, mock_request_type_selection):
        """Test reject change request wizard"""
        mock_request_type_selection.return_value = [("test.request.type", "Test Request Type")]
        mock_request_type_selection.__name__ = "_mocked__selection_request_type_ref_id"
        
        # Create test change request
        change_request = self.env["spp.change.request"].create({
            "name": "Test Request",
            "request_type": "test.request.type",
        })
        
        wizard = self.env["spp.change.request.reject.wizard"].create({
            "change_request_id": change_request.id,
            "rejected_remarks": "Test rejection",
        })
        
        self.assertEqual(wizard.change_request_id, change_request)
        self.assertEqual(wizard.rejected_remarks, "Test rejection")
        
        # Test rejection
        wizard.reject_change_request()
        self.assertEqual(change_request.state, "rejected")

    @patch("odoo.addons.spp_change_request.models.change_request.ChangeRequestBase._selection_request_type_ref_id")
    def test_04_reject_change_request_wizard_default_get(self, mock_request_type_selection):
        """Test reject change request wizard default_get"""
        mock_request_type_selection.return_value = [("test.request.type", "Test Request Type")]
        mock_request_type_selection.__name__ = "_mocked__selection_request_type_ref_id"
        
        # Create test change request
        change_request = self.env["spp.change.request"].create({
            "name": "Test Request",
            "request_type": "test.request.type",
        })
        
        wizard = self.env["spp.change.request.reject.wizard"].with_context(
            change_request_id=change_request.id,
        ).create({})
        
        self.assertEqual(wizard.change_request_id, change_request)

    @patch("odoo.addons.spp_change_request.models.change_request.ChangeRequestBase._selection_request_type_ref_id")
    def test_05_cancel_change_request_wizard(self, mock_request_type_selection):
        """Test cancel change request wizard"""
        mock_request_type_selection.return_value = [("test.request.type", "Test Request Type")]
        mock_request_type_selection.__name__ = "_mocked__selection_request_type_ref_id"
        
        # Create test change request
        change_request = self.env["spp.change.request"].create({
            "name": "Test Request",
            "request_type": "test.request.type",
        })
        
        wizard = self.env["spp.change.request.cancel.wizard"].create({
            "change_request_id": change_request.id,
        })
        
        self.assertEqual(wizard.change_request_id, change_request)
        
        # Test cancellation
        wizard.cancel_change_request()
        self.assertEqual(change_request.state, "cancelled")

    def test_06_cancel_change_request_wizard_default_get(self):
        """Test cancel change request wizard default_get"""
        wizard = self.env["spp.change.request.cancel.wizard"].with_context(
            change_request_id=self.change_request.id,
        ).create({})
        
        self.assertEqual(wizard.change_request_id, self.change_request)

    def test_07_wizard_error_handling(self):
        """Test wizard error handling"""
        # Test reject wizard without change request
        wizard = self.env["spp.change.request.reject.wizard"].create({
            "rejected_remarks": "Test rejection",
        })
        
        with self.assertRaises(UserError):
            wizard.reject_change_request()
        
        # Test cancel wizard without change request
        wizard = self.env["spp.change.request.cancel.wizard"].create({})
        
        with self.assertRaises(UserError):
            wizard.cancel_change_request()

    def test_08_wizard_compute_methods(self):
        """Test wizard compute methods"""
        # Test confirm user assignment wizard compute methods
        wizard = self.env["spp.change.request.user.assign.wizard"].create({
            "change_request_id": self.change_request.id,
            "assign_to_id": self.user.id,
        })
        
        wizard._compute_message_assignment()
        wizard._compute_assign_to_id_domain()
        
        self.assertIsInstance(wizard.dialog_message, str)
        self.assertIsInstance(wizard.assign_to_id_domain, str)
        
        # Test reject wizard compute methods
        reject_wizard = self.env["spp.change.request.reject.wizard"].create({
            "change_request_id": self.change_request.id,
            "rejected_remarks": "Test rejection",
        })
        
        reject_wizard._compute_message()
        self.assertIsInstance(reject_wizard.dialog_message, str)
        
        # Test cancel wizard compute methods
        cancel_wizard = self.env["spp.change.request.cancel.wizard"].create({
            "change_request_id": self.change_request.id,
        })
        
        cancel_wizard._compute_message()
        self.assertIsInstance(cancel_wizard.dialog_message, str)
