from unittest.mock import MagicMock, patch

from frappe.tests.utils import FrappeTestCase

from spp_custom_field.custom_field import create_custom_fields


class TestSPPCustomField(FrappeTestCase):
    def setUp(self):
        # Setup any necessary test data
        pass

    def tearDown(self):
        # Clean up any test data
        pass

    @patch("frappe.get_meta")
    def test_create_custom_fields_new_field(self, mock_get_meta):
        # Mock the get_meta response
        mock_meta = MagicMock()
        mock_meta.get_field.return_value = None
        mock_get_meta.return_value = mock_meta

        # Test data
        custom_fields = [
            {
                "fieldname": "test_field",
                "label": "Test Field",
                "fieldtype": "Data",
                "insert_after": "name",
                "doctype": "Test DocType",
            }
        ]

        with patch("frappe.get_doc") as mock_get_doc:
            mock_doc = MagicMock()
            mock_get_doc.return_value = mock_doc

            # Call the function
            create_custom_fields(custom_fields)

            # Verify create_custom_field was called with correct params
            mock_get_doc.assert_called_once_with(
                {
                    "doctype": "Custom Field",
                    "fieldname": "test_field",
                    "label": "Test Field",
                    "fieldtype": "Data",
                    "insert_after": "name",
                    "dt": "Test DocType",
                }
            )
            mock_doc.insert.assert_called_once()

    @patch("frappe.get_meta")
    def test_create_custom_fields_existing_field(self, mock_get_meta):
        # Mock the get_meta response for existing field
        mock_meta = MagicMock()
        mock_meta.get_field.return_value = True
        mock_get_meta.return_value = mock_meta

        # Test data
        custom_fields = [
            {
                "fieldname": "existing_field",
                "label": "Existing Field",
                "fieldtype": "Data",
                "insert_after": "name",
                "doctype": "Test DocType",
            }
        ]

        # Call the function
        create_custom_fields(custom_fields)

        # Verify no new field was created
        mock_meta.get_field.assert_called_once_with("existing_field")

    @patch("frappe.get_meta")
    def test_create_custom_fields_multiple(self, mock_get_meta):
        # Mock the get_meta response
        mock_meta = MagicMock()
        mock_meta.get_field.return_value = None
        mock_get_meta.return_value = mock_meta

        # Test data with multiple fields
        custom_fields = [
            {
                "fieldname": "test_field_1",
                "label": "Test Field 1",
                "fieldtype": "Data",
                "insert_after": "name",
                "doctype": "Test DocType",
            },
            {
                "fieldname": "test_field_2",
                "label": "Test Field 2",
                "fieldtype": "Select",
                "insert_after": "test_field_1",
                "doctype": "Test DocType",
            },
        ]

        with patch("frappe.get_doc") as mock_get_doc:
            mock_doc = MagicMock()
            mock_get_doc.return_value = mock_doc

            # Call the function
            create_custom_fields(custom_fields)

            # Verify create_custom_field was called twice with correct params
            self.assertEqual(mock_get_doc.call_count, 2)
            mock_doc.insert.assert_called()

    def test_create_custom_fields_invalid_input(self):
        # Test with invalid input
        with self.assertRaises(TypeError):
            create_custom_fields(None)

        with self.assertRaises(ValueError):
            create_custom_fields([])

        with self.assertRaises(TypeError):
            create_custom_fields("not a list")

    @patch("frappe.get_meta")
    def test_create_custom_fields_missing_required_fields(self, mock_get_meta):
        # Test data with missing required fields
        custom_fields = [
            {
                "fieldname": "test_field"
                # Missing other required fields
            }
        ]

        with self.assertRaises(KeyError):
            create_custom_fields(custom_fields)
