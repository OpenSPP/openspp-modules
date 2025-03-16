import frappe
from frappe.tests.utils import FrappeTestCase


class TestSPPCycleAttendanceCompliance(FrappeTestCase):
    def setUp(self):
        # Setup test data
        self.create_test_data()

    def tearDown(self):
        # Clean up test data
        frappe.db.rollback()

    def create_test_data(self):
        # Create test cycle attendance compliance record
        if not frappe.db.exists("SPP Cycle Attendance Compliance", "TEST-CAC-001"):
            self.test_compliance = frappe.get_doc(
                {
                    "doctype": "SPP Cycle Attendance Compliance",
                    "name": "TEST-CAC-001",
                    "cycle": "Test Cycle",
                    "school": "Test School",
                    "attendance_date": "2024-01-01",
                    "compliance_status": "Compliant",
                }
            ).insert(ignore_permissions=True)

    def test_create_cycle_attendance_compliance(self):
        """Test creation of cycle attendance compliance record"""
        compliance = frappe.get_doc(
            {
                "doctype": "SPP Cycle Attendance Compliance",
                "cycle": "Test Cycle 2",
                "school": "Test School 2",
                "attendance_date": "2024-01-02",
                "compliance_status": "Non-Compliant",
            }
        )
        compliance.insert()

        self.assertEqual(compliance.cycle, "Test Cycle 2")
        self.assertEqual(compliance.compliance_status, "Non-Compliant")

    def test_update_compliance_status(self):
        """Test updating compliance status"""
        compliance = frappe.get_doc("SPP Cycle Attendance Compliance", "TEST-CAC-001")
        compliance.compliance_status = "Non-Compliant"
        compliance.save()

        updated_compliance = frappe.get_doc("SPP Cycle Attendance Compliance", "TEST-CAC-001")
        self.assertEqual(updated_compliance.compliance_status, "Non-Compliant")

    def test_validate_attendance_date(self):
        """Test validation of attendance date"""
        with self.assertRaises(frappe.ValidationError):
            frappe.get_doc(
                {
                    "doctype": "SPP Cycle Attendance Compliance",
                    "cycle": "Test Cycle 3",
                    "school": "Test School 3",
                    "attendance_date": "2024-13-01",  # Invalid date
                    "compliance_status": "Compliant",
                }
            ).insert()

    def test_duplicate_record_validation(self):
        """Test validation for duplicate records"""
        with self.assertRaises(frappe.DuplicateEntryError):
            frappe.get_doc(
                {
                    "doctype": "SPP Cycle Attendance Compliance",
                    "cycle": "Test Cycle",
                    "school": "Test School",
                    "attendance_date": "2024-01-01",
                    "compliance_status": "Compliant",
                }
            ).insert()
