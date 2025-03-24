from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import datetime


class TestSPPCycleAttendanceCompliance(TransactionCase):
    def setUp(self):
        super().setUp()
        # Create test data
        self.test_cycle = self.env['spp.cycle.attendance.compliance'].create({
            'cycle': 'Test Cycle 1',
            'school': 'Test School 1',
            'attendance_date': '2024-01-01',
            'compliance_status': 'compliant',
        })

    def test_validate_attendance_date(self):
        """Test that invalid dates raise ValidationError"""
        with self.assertRaises(ValidationError):
            self.env['spp.cycle.attendance.compliance'].create({
                'cycle': 'Test Cycle 3',
                'school': 'Test School 3',
                'attendance_date': '2024-13-01',  # Invalid date
                'compliance_status': 'compliant',
            })

    def test_compute_display_name(self):
        """Test the display name computation"""
        self.assertEqual(
            self.test_cycle.display_name,
            f"{self.test_cycle.cycle} - {self.test_cycle.school}"
        )

    def test_attendance_state_changes(self):
        """Test attendance state transitions"""
        self.assertEqual(self.test_cycle.compliance_status, 'compliant')

        self.test_cycle.write({'compliance_status': 'non_compliant'})
        self.assertEqual(self.test_cycle.compliance_status, 'non_compliant')

    def test_attendance_validation(self):
        """Test attendance validation rules"""
        # Test creating valid record
        valid_record = self.env['spp.cycle.attendance.compliance'].create({
            'cycle': 'Test Cycle 2',
            'school': 'Test School 2',
            'attendance_date': '2024-01-01',
            'compliance_status': 'compliant',
        })
        self.assertTrue(valid_record.id)
