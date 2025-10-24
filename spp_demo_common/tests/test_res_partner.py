# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestResPartner(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )

        # Create a demo data generator for testing
        cls.test_country = cls.env["res.country"].create(
            {
                "name": "Test Country Partner",
                "code": "TP",
                "faker_locale": "en_US",
            }
        )

        cls.generator = cls.env["spp.demo.data.generator"].create(
            {
                "name": "Test Generator",
                "locale_origin": cls.test_country.id,
            }
        )

    def test_01_custom_fields_exist(self):
        """Test that custom partner fields exist"""
        partner = self.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )

        # Check that custom fields exist
        self.assertIn("demo_data_group_generator_id", partner._fields)
        self.assertIn("demo_data_individual_generator_id", partner._fields)
        self.assertIn("gps_coordinates", partner._fields)

    def test_02_create_partner_with_group_generator(self):
        """Test creating partner linked to group generator"""
        partner = self.env["res.partner"].create(
            {
                "name": "Group Generated Partner",
                "demo_data_group_generator_id": self.generator.id,
                "is_group": True,
                "is_registrant": True,
            }
        )

        self.assertEqual(partner.demo_data_group_generator_id, self.generator)
        self.assertTrue(partner.is_group)

    def test_03_create_partner_with_individual_generator(self):
        """Test creating partner linked to individual generator"""
        partner = self.env["res.partner"].create(
            {
                "name": "Individual Generated Partner",
                "demo_data_individual_generator_id": self.generator.id,
                "is_group": False,
                "is_registrant": True,
            }
        )

        self.assertEqual(partner.demo_data_individual_generator_id, self.generator)
        self.assertFalse(partner.is_group)

    def test_04_create_partner_with_gps_coordinates(self):
        """Test creating partner with GPS coordinates"""
        partner = self.env["res.partner"].create(
            {
                "name": "GPS Partner",
                "gps_coordinates": "12.345678, -98.765432",
            }
        )

        self.assertEqual(partner.gps_coordinates, "12.345678, -98.765432")

    def test_05_update_gps_coordinates(self):
        """Test updating partner GPS coordinates"""
        partner = self.env["res.partner"].create(
            {
                "name": "Update GPS Partner",
            }
        )

        partner.write(
            {
                "gps_coordinates": "45.123456, -75.654321",
            }
        )

        self.assertEqual(partner.gps_coordinates, "45.123456, -75.654321")

    def test_06_gps_coordinates_format(self):
        """Test different GPS coordinate formats"""
        # Standard format
        partner1 = self.env["res.partner"].create(
            {
                "name": "GPS Format 1",
                "gps_coordinates": "10.5, 20.5",
            }
        )
        self.assertEqual(partner1.gps_coordinates, "10.5, 20.5")

        # Negative coordinates
        partner2 = self.env["res.partner"].create(
            {
                "name": "GPS Format 2",
                "gps_coordinates": "-10.5, -20.5",
            }
        )
        self.assertEqual(partner2.gps_coordinates, "-10.5, -20.5")

        # High precision
        partner3 = self.env["res.partner"].create(
            {
                "name": "GPS Format 3",
                "gps_coordinates": "12.3456789, -98.7654321",
            }
        )
        self.assertEqual(partner3.gps_coordinates, "12.3456789, -98.7654321")

    def test_07_search_by_generator(self):
        """Test searching partners by generator"""
        self.env["res.partner"].create(
            {
                "name": "Generated Partner 1",
                "demo_data_group_generator_id": self.generator.id,
                "is_group": True,
                "is_registrant": True,
            }
        )
        self.env["res.partner"].create(
            {
                "name": "Generated Partner 2",
                "demo_data_group_generator_id": self.generator.id,
                "is_group": True,
                "is_registrant": True,
            }
        )

        generated_partners = self.env["res.partner"].search([("demo_data_group_generator_id", "=", self.generator.id)])

        self.assertGreaterEqual(len(generated_partners), 2)

    def test_08_generator_relation_group_vs_individual(self):
        """Test that group and individual generator fields are separate"""
        group = self.env["res.partner"].create(
            {
                "name": "Test Group",
                "demo_data_group_generator_id": self.generator.id,
                "is_group": True,
                "is_registrant": True,
            }
        )

        individual = self.env["res.partner"].create(
            {
                "name": "Test Individual",
                "demo_data_individual_generator_id": self.generator.id,
                "is_group": False,
                "is_registrant": True,
            }
        )

        # Group should only have group generator
        self.assertEqual(group.demo_data_group_generator_id, self.generator)
        self.assertFalse(group.demo_data_individual_generator_id)

        # Individual should only have individual generator
        self.assertEqual(individual.demo_data_individual_generator_id, self.generator)
        self.assertFalse(individual.demo_data_group_generator_id)

    def test_09_generated_partners_one2many_relation(self):
        """Test one2many relation from generator to partners"""
        group1 = self.env["res.partner"].create(
            {
                "name": "Generated Group 1",
                "demo_data_group_generator_id": self.generator.id,
                "is_group": True,
                "is_registrant": True,
            }
        )

        group2 = self.env["res.partner"].create(
            {
                "name": "Generated Group 2",
                "demo_data_group_generator_id": self.generator.id,
                "is_group": True,
                "is_registrant": True,
            }
        )

        # Check one2many from generator
        self.assertIn(group1, self.generator.generated_group_ids)
        self.assertIn(group2, self.generator.generated_group_ids)

    def test_10_gps_coordinates_empty_value(self):
        """Test GPS coordinates with empty value"""
        partner = self.env["res.partner"].create(
            {
                "name": "Empty GPS Partner",
                "gps_coordinates": False,
            }
        )

        self.assertFalse(partner.gps_coordinates)

    def test_11_partner_without_generator(self):
        """Test partner without demo generator"""
        partner = self.env["res.partner"].create(
            {
                "name": "Regular Partner",
            }
        )

        self.assertFalse(partner.demo_data_group_generator_id)
        self.assertFalse(partner.demo_data_individual_generator_id)

    def test_12_inherit_model_check(self):
        """Test that res.partner is properly inherited"""
        partner = self.env["res.partner"].create(
            {
                "name": "Inherit Test Partner",
            }
        )

        # Verify standard partner fields still exist
        self.assertIn("name", partner._fields)
        self.assertIn("email", partner._fields)

        # Verify our custom fields are there
        custom_fields = ["demo_data_group_generator_id", "demo_data_individual_generator_id", "gps_coordinates"]
        for field in custom_fields:
            self.assertIn(field, partner._fields)

    def test_13_gps_coordinates_text_field(self):
        """Test that gps_coordinates is a text field"""
        partner = self.env["res.partner"].create(
            {
                "name": "GPS Type Test",
            }
        )

        # Verify field type
        field = partner._fields["gps_coordinates"]
        self.assertEqual(field.type, "text")

    def test_14_generator_fields_readonly(self):
        """Test that generator fields are readonly"""
        partner = self.env["res.partner"].create(
            {
                "name": "Readonly Test",
                "demo_data_group_generator_id": self.generator.id,
            }
        )

        # Check field properties
        group_gen_field = partner._fields["demo_data_group_generator_id"]
        individual_gen_field = partner._fields["demo_data_individual_generator_id"]

        self.assertTrue(group_gen_field.readonly)
        self.assertTrue(individual_gen_field.readonly)

    def test_15_multiple_generators(self):
        """Test partners with different generators"""
        generator1 = self.env["spp.demo.data.generator"].create(
            {
                "name": "Generator 1",
                "locale_origin": self.test_country.id,
            }
        )

        generator2 = self.env["spp.demo.data.generator"].create(
            {
                "name": "Generator 2",
                "locale_origin": self.test_country.id,
            }
        )

        partner1 = self.env["res.partner"].create(
            {
                "name": "Partner from Gen 1",
                "demo_data_group_generator_id": generator1.id,
                "is_group": True,
                "is_registrant": True,
            }
        )

        partner2 = self.env["res.partner"].create(
            {
                "name": "Partner from Gen 2",
                "demo_data_group_generator_id": generator2.id,
                "is_group": True,
                "is_registrant": True,
            }
        )

        self.assertEqual(partner1.demo_data_group_generator_id, generator1)
        self.assertEqual(partner2.demo_data_group_generator_id, generator2)
        self.assertIn(partner1, generator1.generated_group_ids)
        self.assertIn(partner2, generator2.generated_group_ids)
        self.assertNotIn(partner1, generator2.generated_group_ids)
        self.assertNotIn(partner2, generator1.generated_group_ids)
