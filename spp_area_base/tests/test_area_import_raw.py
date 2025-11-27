from .common import AreaImportBaseTestMixin


class BaseAreaImportRawTest(AreaImportBaseTestMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.area_import_raw_data_id = cls.env["spp.area.import.raw"].create(
            {
                "area_import_id": cls.area_import_id.id,
                "admin_name": "Philippines",
                "admin_code": "PH",
                "parent_name": "",
                "parent_code": "",
                "level": 0,
                "area_sqkm": "194000.23",
            }
        )

        cls.area_import_raw_data_child_id = cls.env["spp.area.import.raw"].create(
            {
                "area_import_id": cls.area_import_id.id,
                "admin_name": "Manila",
                "admin_code": "MNL",
                "parent_name": "Philippines",
                "parent_code": "PH",
                "level": 1,
                "area_sqkm": "200.23",
            }
        )

    def test_01_validate_import_raw_data_no_error(self):
        """Test validation of raw data with no errors"""
        result = self.area_import_raw_data_id.validate_raw_data()
        result_child = self.area_import_raw_data_child_id.validate_raw_data()

        self.assertFalse(result)
        self.assertEqual(self.area_import_raw_data_id.state, "Validated")
        self.assertEqual(self.area_import_raw_data_id.remarks, "No Error")

        self.assertFalse(result_child)
        self.assertEqual(self.area_import_raw_data_child_id.state, "Validated")
        self.assertEqual(self.area_import_raw_data_child_id.remarks, "No Error")

    def test_02_validate_import_raw_data_with_error(self):
        """Test validation of raw data with various errors"""
        self.area_import_raw_data_id.admin_name = ""
        self.area_import_raw_data_id.area_sqkm = "text"
        self.area_import_raw_data_id.parent_name = "MNL"
        self.area_import_raw_data_child_id.parent_name = ""

        self.area_import_raw_data_id.validate_raw_data()
        self.area_import_raw_data_child_id.validate_raw_data()

        self.assertEqual(self.area_import_raw_data_id.state, "Error")
        self.assertIn("Name and Code of area is required.", self.area_import_raw_data_id.remarks)
        self.assertIn("AREA_SQKM should be numerical.", self.area_import_raw_data_id.remarks)
        self.assertIn(
            "Level 0 area should not have a parent name and parent code.",
            self.area_import_raw_data_id.remarks,
        )

        self.assertEqual(self.area_import_raw_data_child_id.state, "Error")
        self.assertIn(
            "Level 1 and above area should have a parent name and parent code.",
            self.area_import_raw_data_child_id.remarks,
        )

    def test_03_save_import_to_area(self):
        """Test saving raw data to area"""
        self.area_import_raw_data_id.area_sqkm = ""

        self.area_import_raw_data_id.save_to_area()
        self.assertEqual(self.area_import_raw_data_id.state, "Posted")

        self.area_import_raw_data_id.save_to_area()
        self.assertEqual(self.area_import_raw_data_id.state, "Updated")

    def test_04_check_errors_function(self):
        """Test the check_errors function directly"""
        # Valid data should return empty error list
        errors = self.area_import_raw_data_id.check_errors()
        self.assertEqual(len(errors), 0)

        # Missing name and code
        test_record = self.env["spp.area.import.raw"].create(
            {
                "area_import_id": self.area_import_id.id,
                "admin_name": "",
                "admin_code": "",
                "level": 0,
            }
        )
        errors = test_record.check_errors()
        self.assertTrue(len(errors) > 0)
        self.assertTrue(any("Name and Code" in str(error) for error in errors))

    def test_05_get_area_vals(self):
        """Test the get_area_vals function"""
        area_vals = self.area_import_raw_data_id.get_area_vals()

        # Check that all required fields are present
        self.assertEqual(area_vals["draft_name"], "Philippines")
        self.assertEqual(area_vals["code"], "PH")
        self.assertEqual(area_vals["parent_id"], None)
        self.assertTrue("area_sqkm" in area_vals)
        self.assertTrue("kind" in area_vals)

    def test_06_compute_state_order(self):
        """Test state order computation"""
        # Check that state order is computed correctly
        self.area_import_raw_data_id.state = "New"
        self.area_import_raw_data_id._compute_state_order()
        new_order = self.area_import_raw_data_id.state_order

        self.area_import_raw_data_id.state = "Validated"
        self.area_import_raw_data_id._compute_state_order()
        validated_order = self.area_import_raw_data_id.state_order

        self.area_import_raw_data_id.state = "Error"
        self.area_import_raw_data_id._compute_state_order()
        error_order = self.area_import_raw_data_id.state_order

        # Error should have lowest order (0), then New, then Validated
        self.assertEqual(error_order, 0)
        self.assertTrue(new_order > error_order)
        self.assertTrue(validated_order > new_order)

    def test_07_save_to_area_with_translations(self):
        """Test saving area with multiple language translations"""
        # Activate Arabic language
        lang_ar = self.env["res.lang"].with_context(active_test=False).search([("iso_code", "=", "ar")])
        if lang_ar:
            lang_ar.active = True

            # Set Arabic translation
            self.area_import_raw_data_id.with_context(lang="ar_001").admin_name = "الفلبين"

            # Save to area
            self.area_import_raw_data_id.save_to_area()

            # Check that area was created with translations
            area = self.area_import_raw_data_id.area_id
            self.assertTrue(area)
            self.assertEqual(area.draft_name, "Philippines")

            # Check Arabic translation
            area_ar = area.with_context(lang="ar_001")
            # Translation should be set
            self.assertTrue(area_ar.draft_name)

    def test_08_fix_area_level_and_kind(self):
        """Test fixing area level and kind"""
        # First save to area
        self.area_import_raw_data_id.save_to_area()

        # Now fix level and kind
        self.area_import_raw_data_id.fix_area_level_and_kind()

        # Check that area has correct kind
        area = self.area_import_raw_data_id.area_id
        self.assertTrue(area.kind)

    def test_09_area_sqkm_conversion(self):
        """Test area_sqkm conversion from string to float"""
        # Test with valid number
        test_record = self.env["spp.area.import.raw"].create(
            {
                "area_import_id": self.area_import_id.id,
                "admin_name": "Test Area",
                "admin_code": "TST",
                "level": 0,
                "area_sqkm": "1234.56",
            }
        )
        area_vals = test_record.get_area_vals()
        self.assertEqual(area_vals["area_sqkm"], 1234.56)

        # Test with empty string
        test_record.area_sqkm = ""
        area_vals = test_record.get_area_vals()
        self.assertEqual(area_vals["area_sqkm"], 0.0)

        # Test with invalid string
        test_record.area_sqkm = "not_a_number"
        area_vals = test_record.get_area_vals()
        self.assertEqual(area_vals["area_sqkm"], 0.0)
