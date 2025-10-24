# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestResCountry(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )

    def test_01_custom_fields_exist(self):
        """Test that custom country fields exist"""
        country = self.env["res.country"].create(
            {
                "name": "Test Country",
                "code": "TC",
            }
        )

        # Check that custom fields exist
        self.assertIn("lat_min", country._fields)
        self.assertIn("lat_max", country._fields)
        self.assertIn("lon_min", country._fields)
        self.assertIn("lon_max", country._fields)
        self.assertIn("faker_locale", country._fields)
        self.assertIn("faker_locale_available", country._fields)

    def test_02_create_country_with_gps_bounds(self):
        """Test creating country with GPS bounds"""
        country = self.env["res.country"].create(
            {
                "name": "GPS Bounds Country",
                "code": "GB",
                "lat_min": -10.5,
                "lat_max": 10.5,
                "lon_min": -20.5,
                "lon_max": 20.5,
            }
        )

        self.assertEqual(country.lat_min, -10.5)
        self.assertEqual(country.lat_max, 10.5)
        self.assertEqual(country.lon_min, -20.5)
        self.assertEqual(country.lon_max, 20.5)

    def test_03_create_country_with_faker_locale(self):
        """Test creating country with faker locale"""
        country = self.env["res.country"].create(
            {
                "name": "Faker Locale Country",
                "code": "FL",
                "faker_locale": "en_US",
                "faker_locale_available": True,
            }
        )

        self.assertEqual(country.faker_locale, "en_US")
        self.assertTrue(country.faker_locale_available)

    def test_04_update_country_gps_bounds(self):
        """Test updating country GPS bounds"""
        country = self.env["res.country"].create(
            {
                "name": "Update GPS Country",
                "code": "UG",
            }
        )

        country.write(
            {
                "lat_min": 5.0,
                "lat_max": 15.0,
                "lon_min": 25.0,
                "lon_max": 35.0,
            }
        )

        self.assertEqual(country.lat_min, 5.0)
        self.assertEqual(country.lat_max, 15.0)
        self.assertEqual(country.lon_min, 25.0)
        self.assertEqual(country.lon_max, 35.0)

    def test_05_update_faker_locale(self):
        """Test updating faker locale"""
        country = self.env["res.country"].create(
            {
                "name": "Update Faker Country",
                "code": "UF",
                "faker_locale": "en_US",
            }
        )

        country.write(
            {
                "faker_locale": "fr_FR",
                "faker_locale_available": True,
            }
        )

        self.assertEqual(country.faker_locale, "fr_FR")
        self.assertTrue(country.faker_locale_available)

    def test_06_gps_bounds_negative_values(self):
        """Test GPS bounds with negative values"""
        country = self.env["res.country"].create(
            {
                "name": "Negative GPS Country",
                "code": "NG",
                "lat_min": -50.0,
                "lat_max": -30.0,
                "lon_min": -100.0,
                "lon_max": -80.0,
            }
        )

        self.assertEqual(country.lat_min, -50.0)
        self.assertEqual(country.lat_max, -30.0)
        self.assertEqual(country.lon_min, -100.0)
        self.assertEqual(country.lon_max, -80.0)

    def test_07_gps_bounds_zero_values(self):
        """Test GPS bounds with zero values"""
        country = self.env["res.country"].create(
            {
                "name": "Zero GPS Country",
                "code": "ZG",
                "lat_min": 0.0,
                "lat_max": 0.0,
                "lon_min": 0.0,
                "lon_max": 0.0,
            }
        )

        self.assertEqual(country.lat_min, 0.0)
        self.assertEqual(country.lat_max, 0.0)
        self.assertEqual(country.lon_min, 0.0)
        self.assertEqual(country.lon_max, 0.0)

    def test_08_multiple_countries_different_locales(self):
        """Test multiple countries with different locales"""
        us_country = self.env["res.country"].create(
            {
                "name": "Test United States",
                "code": "TU",
                "faker_locale": "en_US",
                "faker_locale_available": True,
            }
        )

        fr_country = self.env["res.country"].create(
            {
                "name": "Test France",
                "code": "TF",
                "faker_locale": "fr_FR",
                "faker_locale_available": True,
            }
        )

        de_country = self.env["res.country"].create(
            {
                "name": "Test Germany",
                "code": "TG",
                "faker_locale": "de_DE",
                "faker_locale_available": True,
            }
        )

        self.assertEqual(us_country.faker_locale, "en_US")
        self.assertEqual(fr_country.faker_locale, "fr_FR")
        self.assertEqual(de_country.faker_locale, "de_DE")

    def test_09_country_without_optional_fields(self):
        """Test country without optional GPS and faker fields"""
        country = self.env["res.country"].create(
            {
                "name": "Minimal Country",
                "code": "MC",
            }
        )

        # Optional fields should be False/None
        self.assertFalse(country.lat_min)
        self.assertFalse(country.lat_max)
        self.assertFalse(country.lon_min)
        self.assertFalse(country.lon_max)
        self.assertFalse(country.faker_locale)
        self.assertFalse(country.faker_locale_available)

    def test_10_inherit_model_check(self):
        """Test that res.country is properly inherited"""
        country = self.env["res.country"].create(
            {
                "name": "Inherit Test Country",
                "code": "IT",
            }
        )

        # Verify standard country fields still exist
        self.assertIn("name", country._fields)
        self.assertIn("code", country._fields)

        # Verify our custom fields are there
        custom_fields = ["lat_min", "lat_max", "lon_min", "lon_max", "faker_locale", "faker_locale_available"]
        for field in custom_fields:
            self.assertIn(field, country._fields)

    def test_11_search_by_faker_locale(self):
        """Test searching countries by faker locale"""
        self.env["res.country"].create(
            {
                "name": "Search Test 1",
                "code": "S1",
                "faker_locale": "en_US",
            }
        )
        self.env["res.country"].create(
            {
                "name": "Search Test 2",
                "code": "S2",
                "faker_locale": "en_US",
            }
        )
        self.env["res.country"].create(
            {
                "name": "Search Test 3",
                "code": "S3",
                "faker_locale": "fr_FR",
            }
        )

        us_locale_countries = self.env["res.country"].search([("faker_locale", "=", "en_US")])
        self.assertGreaterEqual(len(us_locale_countries), 2)

    def test_12_float_precision_gps_bounds(self):
        """Test GPS bounds with high precision floats"""
        country = self.env["res.country"].create(
            {
                "name": "Precision GPS Country",
                "code": "PG",
                "lat_min": 12.345678,
                "lat_max": 12.876543,
                "lon_min": -98.765432,
                "lon_max": -98.234567,
            }
        )

        # Check precision is maintained
        self.assertAlmostEqual(country.lat_min, 12.345678, places=6)
        self.assertAlmostEqual(country.lat_max, 12.876543, places=6)
        self.assertAlmostEqual(country.lon_min, -98.765432, places=6)
        self.assertAlmostEqual(country.lon_max, -98.234567, places=6)
