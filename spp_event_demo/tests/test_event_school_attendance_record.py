import logging

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class EventSchoolAttendanceRecordTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(EventSchoolAttendanceRecordTest, cls).setUpClass()

        # Initial Setup of Variables
        cls.person_1 = cls.env["res.partner"].create(
            {
                "name": "Person 1",
                "is_registrant": True,
                "is_group": False,
            }
        )
        cls.school_attendance_1 = cls.env["spp.event.schoolattendance.record"].create(
            {
                "attendance_description": "Enrolled in secondary school",
                "date": "2023-10-24",
            }
        )
        cls.event_data_1 = cls.env["spp.event.data"].create(
            {
                "partner_id": cls.person_1.id,
                "model": "spp.event.schoolattendance.record",
                "res_id": cls.school_attendance_1.id,
            }
        )

    def test_01_check_active_school_attendance_record(self):
        self.person_1._compute_active_school_attendance_record()
        self.assertEqual(
            self.person_1.active_school_attendance_record.id,
            self.event_data_1.id,
        )

    def test_02_check_description(self):
        self.assertIn(
            "School Attendance Record",
            self.person_1.active_school_attendance_record.name,
        )

    def test_03_recheck_active_phone_survey_after_entering_new_visit(self):
        vals_school = {
            "attendance_description": "Enrolled in university",
            "date": "2028-10-24",
        }
        school_attendance_report_2 = self.env[
            "spp.event.schoolattendance.record"
        ].create(vals_school)

        vals_event_data = {
            "partner_id": self.person_1.id,
            "model": "spp.event.schoolattendance.record",
            "res_id": school_attendance_report_2.id,
        }
        event_data_2 = self.env["spp.event.data"].create(vals_event_data)
        self.person_1._compute_active_school_attendance_record()
        self.assertEqual(
            self.person_1.active_school_attendance_record.id,
            event_data_2.id,
        )
