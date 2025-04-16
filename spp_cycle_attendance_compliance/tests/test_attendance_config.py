from psycopg2.errors import NotNullViolation, UniqueViolation

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase
from odoo.tools.misc import mute_logger


class TestAttendanceConfig(TransactionCase):
    def setUp(self):
        super().setUp()

    def test_01_create_attendance_type(self):
        """Test creating attendance type"""
        attendance_type = self.env["spp.res.config.attendance.type"].create(
            {
                "name": "Test Type",
                "description": "Test Description",
                "external_id": 1,
                "external_source": "http://test.com",
            }
        )

        self.assertTrue(attendance_type, "Attendance type should be created")
        self.assertEqual(attendance_type.name, "Test Type", "Name should match")
        self.assertEqual(attendance_type.description, "Test Description", "Description should match")
        self.assertEqual(attendance_type.external_id, 1, "External ID should match")
        self.assertEqual(attendance_type.external_source, "http://test.com", "External source should match")
        self.assertFalse(attendance_type.set_as_default, "Default should be False initially")

    @mute_logger("odoo.sql_db")
    def test_02_duplicate_attendance_type_name(self):
        """Test duplicate attendance type name validation"""
        # Create first record
        attendance_type1 = self.env["spp.res.config.attendance.type"].create(
            {
                "name": "Test Type 1",
                "external_id": 1,
                "external_source": "http://test.com",
            }
        )
        self.assertTrue(attendance_type1, "First attendance type should be created")

        # Try to create second record with same name - should fail
        with self.assertRaises(UniqueViolation):
            self.env.cr.execute(
                """
                INSERT INTO spp_res_config_attendance_type
                (name, external_id, external_source, create_uid, create_date, write_uid, write_date)
                VALUES ('Test Type 1', 2, 'http://test.com', 1, now(), 1, now())
            """
            )
            self.env.cr.commit()  # Need to commit to see the UniqueViolation

    @mute_logger("odoo.sql_db")
    def test_03_attendance_type_required_fields(self):
        """Test required fields validation for attendance type"""
        # Test missing name
        with self.assertRaises(NotNullViolation):
            self.env.cr.execute(
                """
                INSERT INTO spp_res_config_attendance_type
                (external_id, external_source, create_uid, create_date, write_uid, write_date)
                VALUES (1, 'http://test.com', 1, now(), 1, now())
            """
            )
            self.env.cr.commit()

        # Test missing external_id
        with self.assertRaises(NotNullViolation):
            self.env.cr.execute(
                """
                INSERT INTO spp_res_config_attendance_type
                (name, external_source, create_uid, create_date, write_uid, write_date)
                VALUES ('Test Type', 'http://test.com', 1, now(), 1, now())
            """
            )
            self.env.cr.commit()

        # Test missing external_source
        with self.assertRaises(NotNullViolation):
            self.env.cr.execute(
                """
                INSERT INTO spp_res_config_attendance_type
                (name, external_id, create_uid, create_date, write_uid, write_date)
                VALUES ('Test Type', 1, 1, now(), 1, now())
            """
            )
            self.env.cr.commit()

    def test_04_attendance_type_default_setting(self):
        """Test set_as_default functionality for attendance type"""
        # Create first record and set as default
        type1 = self.env["spp.res.config.attendance.type"].create(
            {
                "name": "Type 1",
                "external_id": 1,
                "external_source": "http://test.com",
                "set_as_default": True,
            }
        )
        self.assertTrue(type1.set_as_default, "First record should be set as default")

        # Create second record and try to set as default
        type2 = self.env["spp.res.config.attendance.type"].create(
            {
                "name": "Type 2",
                "external_id": 2,
                "external_source": "http://test.com",
            }
        )

        # Trying to set second record as default should raise error
        with self.assertRaises(ValidationError):
            type2.write({"set_as_default": True})

        # Unset first record as default
        type1.write({"set_as_default": False})

        # Now setting second record as default should work
        type2.write({"set_as_default": True})
        self.assertTrue(type2.set_as_default, "Second record should now be set as default")
        self.assertFalse(type1.set_as_default, "First record should no longer be default")

    def test_05_create_attendance_location(self):
        """Test creating attendance location"""
        location = self.env["spp.res.config.attendance.location"].create(
            {
                "name": "Test Location",
                "description": "Test Location Description",
                "external_id": 1,
                "external_source": "http://test.com",
            }
        )

        self.assertTrue(location, "Attendance location should be created")
        self.assertEqual(location.name, "Test Location", "Name should match")
        self.assertEqual(location.description, "Test Location Description", "Description should match")
        self.assertEqual(location.external_id, 1, "External ID should match")
        self.assertEqual(location.external_source, "http://test.com", "External source should match")

    @mute_logger("odoo.sql_db")
    def test_06_duplicate_location_name(self):
        """Test duplicate location name validation"""
        # Create first record
        location1 = self.env["spp.res.config.attendance.location"].create(
            {
                "name": "Test Location 1",
                "external_id": 1,
                "external_source": "http://test.com",
            }
        )
        self.assertTrue(location1, "First location should be created")

        # Try to create second record with same name - should fail
        with self.assertRaises(UniqueViolation):
            self.env.cr.execute(
                """
                INSERT INTO spp_res_config_attendance_location
                (name, external_id, external_source, create_uid, create_date, write_uid, write_date)
                VALUES ('Test Location 1', 2, 'http://test.com', 1, now(), 1, now())
            """
            )
            self.env.cr.commit()  # Need to commit to see the UniqueViolation

    @mute_logger("odoo.sql_db")
    def test_07_location_required_fields(self):
        """Test required fields validation for location"""
        # Test missing name
        with self.assertRaises(NotNullViolation):
            self.env.cr.execute(
                """
                INSERT INTO spp_res_config_attendance_location
                (external_id, external_source, create_uid, create_date, write_uid, write_date)
                VALUES (1, 'http://test.com', 1, now(), 1, now())
            """
            )
            self.env.cr.commit()

        # Test missing external_id
        with self.assertRaises(NotNullViolation):
            self.env.cr.execute(
                """
                INSERT INTO spp_res_config_attendance_location
                (name, external_source, create_uid, create_date, write_uid, write_date)
                VALUES ('Test Location', 'http://test.com', 1, now(), 1, now())
            """
            )
            self.env.cr.commit()

        # Test missing external_source
        with self.assertRaises(NotNullViolation):
            self.env.cr.execute(
                """
                INSERT INTO spp_res_config_attendance_location
                (name, external_id, create_uid, create_date, write_uid, write_date)
                VALUES ('Test Location', 1, 1, now(), 1, now())
            """
            )
            self.env.cr.commit()

    def test_08_edge_cases(self):
        """Test edge cases for both models"""
        # Test special characters in name
        special_name = "Test@#$%^&*()"
        location = self.env["spp.res.config.attendance.location"].create(
            {
                "name": special_name,
                "external_id": 1,
                "external_source": "http://test.com",
            }
        )
        self.assertEqual(location.name, special_name, "Special characters should be allowed in name")

        # Test empty description (should be allowed)
        type_empty_desc = self.env["spp.res.config.attendance.type"].create(
            {
                "name": "Test Empty Desc",
                "description": "",
                "external_id": 1,
                "external_source": "http://test.com",
            }
        )
        self.assertEqual(type_empty_desc.description, "", "Empty description should be allowed")
