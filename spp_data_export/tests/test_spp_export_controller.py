import json
import logging
from unittest.mock import patch, MagicMock

from odoo import _
from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)

EXCEL_ROW_LIMIT = 1_048_576


@tagged("post_install", "-at_install")
class TestSppExportController(TransactionCase):
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

    def setUp(self):
        super().setUp()
        # Import the controller class
        from odoo.addons.spp_data_export.controllers.main import SppExport
        self.SppExport = SppExport

    def _test_validation_logic(self, test_data, expected_behavior, expected_error=None):
        """Helper method to test the validation logic"""
        # Mock the search_count to return the expected value
        if expected_behavior == "pass":
            with patch.object(self.env[test_data.get("model", "res.partner")], 'search_count', return_value=1000):
                # Create controller instance
                controller = self.SppExport()
                
                # Mock the parent class method
                with patch('builtins.super') as mock_super:
                    mock_super_instance = MagicMock()
                    mock_super_instance.index.return_value = "success"
                    mock_super.return_value = mock_super_instance
                    
                    # Call the controller method
                    result = controller.index(json.dumps(test_data))
                    
                    # Should call super().index() after validation passes
                    mock_super_instance.index.assert_called_once_with(json.dumps(test_data))
                    self.assertEqual(result, "success")
        
        elif expected_behavior == "fail":
            with patch.object(self.env[test_data.get("model", "res.partner")], 'search_count', return_value=EXCEL_ROW_LIMIT + 1):
                # Create controller instance
                controller = self.SppExport()
                
                with self.assertRaises(ValidationError) as context:
                    controller.index(json.dumps(test_data))
                
                # Verify the error message contains the expected information
                error_message = str(context.exception)
                self.assertIn("The number of record surpasses the limitation of Excel 2007-2013 (.xlsx) format", error_message)
                self.assertIn(str(EXCEL_ROW_LIMIT + 1), error_message)
                self.assertIn(str(EXCEL_ROW_LIMIT), error_message)
                self.assertIn("Please consider splitting the export", error_message)

    def test_01_export_with_ids_should_bypass_validation(self):
        """Test that export with specific IDs bypasses the row limit check"""
        test_data = {
            "ids": [1, 2, 3],
            "model": "res.partner",
            "domain": [],
        }
        
        # Create controller instance
        controller = self.SppExport()
        
        # Mock the parent class method to avoid calling the actual Excel export
        with patch('builtins.super') as mock_super:
            mock_super_instance = MagicMock()
            mock_super_instance.index.return_value = "success"
            mock_super.return_value = mock_super_instance
            
            # Call the controller method
            result = controller.index(json.dumps(test_data))
            
            # Should call super().index() without any validation
            mock_super_instance.index.assert_called_once_with(json.dumps(test_data))
            self.assertEqual(result, "success")

    def test_02_export_with_domain_under_limit_should_pass_through(self):
        """Test that export with domain under Excel row limit passes through"""
        test_data = {
            "ids": None,
            "model": "res.partner",
            "domain": [("name", "ilike", "test")],
        }
        
        self._test_validation_logic(test_data, "pass")

    def test_03_export_with_domain_at_limit_should_pass_through(self):
        """Test that export with domain at exactly Excel row limit passes through"""
        # Mock the search_count to return exactly the limit
        with patch.object(self.env['res.partner'], 'search_count', return_value=EXCEL_ROW_LIMIT):
            test_data = {
                "ids": None,
                "model": "res.partner",
                "domain": [("name", "ilike", "test")],
            }
            
            # Create controller instance
            controller = self.SppExport()
            
            # Mock the parent class method
            with patch('builtins.super') as mock_super:
                mock_super_instance = MagicMock()
                mock_super_instance.index.return_value = "success"
                mock_super.return_value = mock_super_instance
                
                # Call the controller method
                result = controller.index(json.dumps(test_data))
                
                # Should call super().index() after validation passes
                mock_super_instance.index.assert_called_once_with(json.dumps(test_data))
                self.assertEqual(result, "success")

    def test_04_export_with_domain_over_limit_should_raise_error(self):
        """Test that export with domain over Excel row limit raises ValidationError"""
        test_data = {
            "ids": None,
            "model": "res.partner",
            "domain": [("name", "ilike", "test")],
        }
        
        self._test_validation_logic(test_data, "fail")

    def test_05_export_with_domain_significantly_over_limit_should_raise_error(self):
        """Test that export with domain significantly over Excel row limit raises ValidationError"""
        # Mock the search_count to return a much larger value
        large_count = EXCEL_ROW_LIMIT * 2
        with patch.object(self.env['res.partner'], 'search_count', return_value=large_count):
            test_data = {
                "ids": None,
                "model": "res.partner",
                "domain": [("name", "ilike", "test")],
            }
            
            # Create controller instance
            controller = self.SppExport()
            
            with self.assertRaises(ValidationError) as context:
                controller.index(json.dumps(test_data))
            
            # Verify the error message contains the expected information
            error_message = str(context.exception)
            self.assertIn("The number of record surpasses the limitation of Excel 2007-2013 (.xlsx) format", error_message)
            self.assertIn(str(large_count), error_message)
            self.assertIn(str(EXCEL_ROW_LIMIT), error_message)

    def test_06_export_with_empty_domain_should_work(self):
        """Test that export with empty domain works correctly"""
        test_data = {
            "ids": None,
            "model": "res.partner",
            "domain": [],
        }
        
        self._test_validation_logic(test_data, "pass")

    def test_07_export_with_complex_domain_should_work(self):
        """Test that export with complex domain works correctly"""
        test_data = {
            "ids": None,
            "model": "res.partner",
            "domain": [
                ("name", "ilike", "test"),
                ("is_company", "=", True),
                ("active", "=", True)
            ],
        }
        
        self._test_validation_logic(test_data, "pass")

    def test_08_export_with_different_model_should_work(self):
        """Test that export with different model works correctly"""
        test_data = {
            "ids": None,
            "model": "res.users",
            "domain": [("active", "=", True)],
        }
        
        self._test_validation_logic(test_data, "pass")

    def test_09_export_with_missing_model_should_raise_error(self):
        """Test that export with missing model raises appropriate error"""
        test_data = {
            "ids": None,
            "domain": [("name", "ilike", "test")],
            # Missing "model" key
        }
        
        # Create controller instance
        controller = self.SppExport()
        
        with self.assertRaises(KeyError):
            controller.index(json.dumps(test_data))

    def test_10_export_with_invalid_json_should_raise_error(self):
        """Test that export with invalid JSON raises appropriate error"""
        invalid_json = "{invalid json}"
        
        # Create controller instance
        controller = self.SppExport()
        
        with self.assertRaises(json.JSONDecodeError):
            controller.index(invalid_json)

    def test_11_export_with_none_data_should_raise_error(self):
        """Test that export with None data raises appropriate error"""
        # Create controller instance
        controller = self.SppExport()
        
        with self.assertRaises(TypeError):
            controller.index(None)

    def test_12_export_with_empty_string_data_should_raise_error(self):
        """Test that export with empty string data raises appropriate error"""
        # Create controller instance
        controller = self.SppExport()
        
        with self.assertRaises(json.JSONDecodeError):
            controller.index("")

    def test_13_export_with_falsy_ids_should_check_domain(self):
        """Test that export with falsy IDs (empty list, None, etc.) checks domain"""
        test_cases = [
            {"ids": [], "model": "res.partner", "domain": [("name", "ilike", "test")]},
            {"ids": None, "model": "res.partner", "domain": [("name", "ilike", "test")]},
            {"ids": False, "model": "res.partner", "domain": [("name", "ilike", "test")]},
        ]
        
        for test_data in test_cases:
            self._test_validation_logic(test_data, "pass")

    def test_14_export_with_truthy_ids_should_bypass_check(self):
        """Test that export with truthy IDs bypasses domain check"""
        test_cases = [
            {"ids": [1], "model": "res.partner", "domain": [("name", "ilike", "test")]},
            {"ids": [1, 2, 3], "model": "res.partner", "domain": [("name", "ilike", "test")]},
        ]
        
        for test_data in test_cases:
            # Create controller instance
            controller = self.SppExport()
            
            # Mock the parent class method
            with patch('builtins.super') as mock_super:
                mock_super_instance = MagicMock()
                mock_super_instance.index.return_value = "success"
                mock_super.return_value = mock_super_instance
                
                # Call the controller method
                result = controller.index(json.dumps(test_data))
                
                # Should call super().index() without any validation
                mock_super_instance.index.assert_called_once_with(json.dumps(test_data))
                self.assertEqual(result, "success")

    def test_15_export_with_search_count_exception_should_raise_error(self):
        """Test that export with search_count exception raises appropriate error"""
        # Mock the search_count to raise an exception
        with patch.object(self.env['res.partner'], 'search_count', side_effect=Exception("Database error")):
            test_data = {
                "ids": None,
                "model": "res.partner",
                "domain": [("name", "ilike", "test")],
            }
            
            # Create controller instance
            controller = self.SppExport()
            
            with self.assertRaises(Exception) as context:
                controller.index(json.dumps(test_data))
            
            self.assertEqual(str(context.exception), "Database error")

    def test_16_export_with_sudo_search_count_should_work(self):
        """Test that export uses sudo() for search_count as expected"""
        # Mock the search_count to verify it's called correctly
        with patch.object(self.env['res.partner'], 'search_count', return_value=100) as mock_search_count:
            test_data = {
                "ids": None,
                "model": "res.partner",
                "domain": [("name", "ilike", "test")],
            }
            
            # Create controller instance
            controller = self.SppExport()
            
            # Mock the parent class method
            with patch('builtins.super') as mock_super:
                mock_super_instance = MagicMock()
                mock_super_instance.index.return_value = "success"
                mock_super.return_value = mock_super_instance
                
                # Call the controller method
                result = controller.index(json.dumps(test_data))
                
                # Verify search_count was called with the correct domain
                mock_search_count.assert_called_once_with([("name", "ilike", "test")])
                self.assertEqual(result, "success")

    def test_17_export_with_edge_case_record_count(self):
        """Test export with edge case record counts around the limit"""
        edge_cases = [
            (EXCEL_ROW_LIMIT - 1, False),  # Just under limit - should pass
            (EXCEL_ROW_LIMIT, False),      # Exactly at limit - should pass
            (EXCEL_ROW_LIMIT + 1, True),   # Just over limit - should fail
        ]
        
        for record_count, should_fail in edge_cases:
            with patch.object(self.env['res.partner'], 'search_count', return_value=record_count):
                test_data = {
                    "ids": None,
                    "model": "res.partner",
                    "domain": [("name", "ilike", "test")],
                }
                
                # Create controller instance
                controller = self.SppExport()
                
                if should_fail:
                    with self.assertRaises(ValidationError) as context:
                        controller.index(json.dumps(test_data))
                    
                    error_message = str(context.exception)
                    self.assertIn(str(record_count), error_message)
                    self.assertIn(str(EXCEL_ROW_LIMIT), error_message)
                else:
                    # Mock the parent class method
                    with patch('builtins.super') as mock_super:
                        mock_super_instance = MagicMock()
                        mock_super_instance.index.return_value = "success"
                        mock_super.return_value = mock_super_instance
                        
                        # Call the controller method
                        result = controller.index(json.dumps(test_data))
                        
                        # Should call super().index() after validation passes
                        mock_super_instance.index.assert_called_once_with(json.dumps(test_data))
                        self.assertEqual(result, "success")

    def test_18_export_with_zero_records_should_pass(self):
        """Test that export with zero records passes through"""
        test_data = {
            "ids": None,
            "model": "res.partner",
            "domain": [("name", "ilike", "nonexistent")],
        }
        
        self._test_validation_logic(test_data, "pass")

    def test_19_export_with_large_negative_records_should_pass(self):
        """Test that export with negative record count (edge case) passes through"""
        # Mock the search_count to return a negative value (edge case)
        with patch.object(self.env['res.partner'], 'search_count', return_value=-100):
            test_data = {
                "ids": None,
                "model": "res.partner",
                "domain": [("name", "ilike", "test")],
            }
            
            # Create controller instance
            controller = self.SppExport()
            
            # Mock the parent class method
            with patch('builtins.super') as mock_super:
                mock_super_instance = MagicMock()
                mock_super_instance.index.return_value = "success"
                mock_super.return_value = mock_super_instance
                
                # Call the controller method
                result = controller.index(json.dumps(test_data))
                
                # Should call super().index() after validation passes (negative < limit)
                mock_super_instance.index.assert_called_once_with(json.dumps(test_data))
                self.assertEqual(result, "success") 