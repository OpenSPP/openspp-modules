import json

from odoo.tests.common import TransactionCase


class FarmTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create required reference data
        cls.gender_male = cls.env["gender.type"].create({"code": "M", "value": "male"})

        cls.gender_female = cls.env["gender.type"].create({"code": "F", "value": "female"})

        # Create group membership kind for head
        cls.head_membership_kind = cls.env["g2p.group.membership.kind"].search([("name", "=", "Head")], limit=1)

        # Create required models for farm inheritance
        cls.land_record = cls.env["spp.land.record"].create(
            {"land_name": "Test Land", "land_acreage": 10.5, "land_use": "cultivation"}
        )

        cls.farm_details = cls.env["spp.farm.details"].create(
            {"details_farm_type": "crop", "farm_total_size": 10.5, "details_legal_status": "self"}
        )

        cls.farmer = cls.env["spp.farmer"].create(
            {
                "farmer_family_name": "Test",
                "farmer_given_name": "Farmer",
                "farmer_mobile_tel": "09123456789",
            }
        )

        # Create individual registrant
        cls.individual = cls.env["res.partner"].create(
            {
                "family_name": "Franco",
                "given_name": "Chin",
                "name": "Chin Franco",
                "is_group": False,
                "is_registrant": True,
                "gender": cls.gender_male.id,
                "marital_status": "single",
                "farmer_household_size": 5,
                "farmer_postal_address": "123 Test Street",
                "email": "test@example.com",
                "formal_agricultural_training": True,
                "highest_education_level": "secondary",
            }
        )

        # Create farm with all required fields
        cls.farm = cls.env["res.partner"].create(
            {
                "name": "Test Farm",
                "is_group": True,
                "is_registrant": True,
                "farmer_family_name": "John",
                "farmer_given_name": "Franco",
                "farmer_mobile_tel": "09123456789",
                "farmer_sex": cls.gender_male.id,
                "farmer_birthdate": "1990-01-01",
                "farmer_household_size": 4,
                "farmer_postal_address": "456 Farm Road",
                "farmer_email": "farmer@example.com",
                "farmer_formal_agricultural": True,
                "farmer_highest_education_level": "primary",
                "farmer_marital_status": "married",
                "farm_detail_id": cls.farm_details.id,
                "farm_land_rec_id": cls.land_record.id,
                "farmer_id": cls.farmer.id,
            }
        )

        cls.individual2 = cls.farm.farmer_individual_id

        # Create group membership for the farm
        cls.group_membership = cls.env["g2p.group.membership"].create(
            {"group": cls.farm.id, "individual": cls.individual.id}
        )

    def test_01_create_farm(self):
        """Test farm creation with all required fields"""
        farm_vals = {
            "name": "New Test Farm",
            "is_group": True,
            "is_registrant": True,
            "farmer_family_name": "Smith",
            "farmer_given_name": "John",
            "farmer_mobile_tel": "09876543210",
            "farmer_sex": self.gender_male.id,
            "farm_detail_id": self.farm_details.id,
            "farm_land_rec_id": self.land_record.id,
            "farmer_id": self.farmer.id,
        }

        new_farm = self.env["res.partner"].create(farm_vals)
        self.assertTrue(new_farm.id)
        self.assertEqual(new_farm.name, "New Test Farm")
        self.assertTrue(new_farm.is_group)
        self.assertTrue(new_farm.is_registrant)

    # def test_02_get_group_head_member(self):
    #     """Test getting group head member"""
    #     head_member = self.farm.get_group_head_member()
    #     # self.assertIsNotNone(head_member)
    #     self.assertEqual(head_member.id, self.individual2.id)
    #     self.assertEqual(head_member.name, "John, Franco ")

    def test_03_get_group_head_member_no_group(self):
        """Test getting group head member for non-group"""
        head_member = self.individual.get_group_head_member()
        self.assertIsNone(head_member)

    def test_04_write_farm(self):
        """Test writing to farm record"""
        original_name = self.farm.name
        self.farm.write({"name": "Updated Farm Name"})
        self.assertEqual(self.farm.name, "Updated Farm Name")
        self.assertNotEqual(self.farm.name, original_name)

    # def test_05_create_update_farmer(self):
    #     """Test creating/updating farmer from farm"""
    #     # Test creating new farmer individual
    #     farm_without_individual = self.env["res.partner"].create(
    #         {
    #             "name": "Farm Without Individual",
    #             "is_group": True,
    #             "is_registrant": True,
    #             "farmer_family_name": "Doe",
    #             "farmer_given_name": "Jane",
    #             "farmer_mobile_tel": "09111111111",
    #             "farmer_sex": self.gender_female.id,
    #             "farm_detail_id": self.farm_details.id,
    #             "farm_land_rec_id": self.land_record.id,
    #             "farmer_id": self.farmer.id,
    #         }
    #     )

    #     # This should create a new individual
    #     self.assertTrue(farm_without_individual.farmer_individual_id)

    # Call the method directly
    # farm_without_individual.create_update_farmer(farm_without_individual)

    # Verify individual was created
    # self.assertTrue(farm_without_individual.farmer_individual_id)
    # self.assertEqual(farm_without_individual.farmer_individual_id.family_name, "Doe")
    # self.assertEqual(farm_without_individual.farmer_individual_id.given_name, "Jane")

    def test_06_insert_phone_number(self):
        """Test inserting phone number"""
        # Test creating new phone number
        self.farm.insert_phone_number(self.individual.id, "09999999999")

        phone_record = self.env["g2p.phone.number"].search([("partner_id", "=", self.individual.id)], limit=1)

        self.assertTrue(phone_record)
        self.assertEqual(phone_record.phone_no, "09999999999")

        # Test updating existing phone number
        self.farm.insert_phone_number(self.individual.id, "08888888888")
        self.assertEqual(phone_record.phone_no, "08888888888")

    def test_08_update_farmer(self):
        """Test updating farmer from individual"""
        # Create phone number and ID for individual
        self.env["g2p.phone.number"].create({"partner_id": self.individual.id, "phone_no": "07777777777"})

        # Create farmer record for individual
        individual_farmer = self.env["spp.farmer"].create(
            {"farmer_family_name": "Individual", "farmer_given_name": "Farmer"}
        )
        self.individual.farmer_id = individual_farmer.id

        # Update farmer
        self.farm.update_farmer(self.individual)

        # Verify farmer record was updated
        self.assertEqual(individual_farmer.farmer_family_name, "Franco")
        self.assertEqual(individual_farmer.farmer_given_name, "Chin")
        self.assertEqual(individual_farmer.farmer_mobile_tel, "07777777777")

    def test_09_get_geojson(self):
        """Test generating GeoJSON from farms"""
        # Add coordinates to farm using proper GeoJSON format
        self.farm.coordinates = '{"type": "Point", "coordinates": [1.0, 1.0]}'

        geojson = self.farm.get_geojson()
        geojson_data = json.loads(geojson)

        self.assertEqual(geojson_data["type"], "FeatureCollection")
        self.assertIn("features", geojson_data)
        self.assertIsInstance(geojson_data["features"], list)

    def test_10_process_record_to_feature(self):
        """Test processing record to GeoJSON feature"""
        # Create transformer
        import pyproj

        proj_from = pyproj.Proj("epsg:3857")
        proj_to = pyproj.Proj("epsg:4326")
        transformer = pyproj.Transformer.from_proj(proj_from, proj_to, always_xy=True).transform

        # Test with coordinates using proper GeoJSON format
        self.farm.coordinates = '{"type": "Point", "coordinates": [1.0, 1.0]}'
        feature = self.farm._process_record_to_feature(self.farm, transformer)

        self.assertIsNotNone(feature)
        self.assertEqual(feature["type"], "Feature")
        self.assertIn("geometry", feature)
        self.assertIn("properties", feature)
        self.assertEqual(feature["properties"]["name"], "Test Farm")

        # Test without coordinates
        self.farm.coordinates = False
        feature = self.farm._process_record_to_feature(self.farm, transformer)
        self.assertIsNone(feature)

    # def test_11_create_update_farmer_with_existing_individual(self):
    #     """Test creating/updating farmer when individual already exists"""
    #     # Set existing individual
    #     self.farm.farmer_individual_id = self.individual.id

    #     # Update farmer details
    #     self.farm.farmer_family_name = "Updated"
    #     self.farm.farmer_given_name = "Name"

    #     # Call the method
    #     self.farm.create_update_farmer(self.farm)

    #     # Verify individual was updated
    #     self.assertEqual(self.individual2.family_name, "Updated")
    #     self.assertEqual(self.individual2.given_name, "Name")

    def test_12_create_update_farmer_with_additional_name(self):
        """Test creating farmer with additional name"""
        farm_with_addl_name = self.env["res.partner"].create(
            {
                "name": "Farm With Additional Name",
                "is_group": True,
                "is_registrant": True,
                "farmer_family_name": "Smith",
                "farmer_given_name": "John",
                "farmer_addtnl_name": "Middle",
                "farmer_mobile_tel": "09111111111",
                "farmer_sex": self.gender_male.id,
                "farm_detail_id": self.farm_details.id,
                "farm_land_rec_id": self.land_record.id,
                "farmer_id": self.farmer.id,
            }
        )

        farm_with_addl_name.create_update_farmer(farm_with_addl_name)

        # Verify individual was created with correct name
        self.assertTrue(farm_with_addl_name.farmer_individual_id)
        individual = farm_with_addl_name.farmer_individual_id
        self.assertEqual(individual.family_name, "Smith")
        self.assertEqual(individual.given_name, "John")
        self.assertEqual(individual.addl_name, "Middle")
        self.assertEqual(individual.name, "Smith, John Middle")

    def test_13_insert_phone_number_empty(self):
        """Test inserting empty phone number"""
        # Should not create phone record for empty number
        self.farm.insert_phone_number(self.individual.id, "")

        phone_record = self.env["g2p.phone.number"].search([("partner_id", "=", self.individual.id)], limit=1)

        self.assertFalse(phone_record)

    def test_15_update_farmer_no_phone_or_id(self):
        """Test updating farmer when individual has no phone or ID"""
        # Create farmer record for individual
        individual_farmer = self.env["spp.farmer"].create(
            {"farmer_family_name": "Individual", "farmer_given_name": "Farmer"}
        )
        self.individual.farmer_id = individual_farmer.id

        # Update farmer (should handle missing phone/ID gracefully)
        self.farm.update_farmer(self.individual)

        # Verify farmer record was updated with basic info
        self.assertEqual(individual_farmer.farmer_family_name, "Franco")
        self.assertEqual(individual_farmer.farmer_given_name, "Chin")

    def test_16_farm_with_coordinates_geojson(self):
        """Test GeoJSON generation with farm coordinates"""
        # Set coordinates using proper GeoJSON format
        self.farm.coordinates = '{"type": "Point", "coordinates": [2.0, 3.0]}'

        geojson = self.farm.get_geojson()
        geojson_data = json.loads(geojson)

        # Should have at least one feature
        self.assertGreater(len(geojson_data["features"]), 0)

        # Check feature structure
        feature = geojson_data["features"][0]
        self.assertEqual(feature["type"], "Feature")
        self.assertIn("geometry", feature)
        self.assertIn("properties", feature)
        self.assertEqual(feature["properties"]["name"], "Test Farm")

    def test_17_farm_without_coordinates_geojson(self):
        """Test GeoJSON generation without farm coordinates"""
        # Remove coordinates
        self.farm.coordinates = False

        geojson = self.farm.get_geojson()
        geojson_data = json.loads(geojson)

        # Should still have FeatureCollection structure
        self.assertEqual(geojson_data["type"], "FeatureCollection")
        self.assertIn("features", geojson_data)
        # But may have no features if no coordinates
        self.assertIsInstance(geojson_data["features"], list)
