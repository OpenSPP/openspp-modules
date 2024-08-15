from odoo.tests.common import TransactionCase


class IndividualTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """
        Setup and create necessary records for this test
        """
        super().setUpClass()
        cls.id_type_id = cls.env["g2p.id.type"].create(
            {
                "name": "National ID",
            }
        )

        cls.individual_id = cls.env["res.partner"].create(
            {
                "name": "Chin Franco",
                "family_name": "Franco",
                "given_name": "Chin",
                "addl_name": "Chin",
                "is_group": False,
                "is_registrant": True,
                "phone": "+639266716911",
            }
        )

        cls.individual_2_id = cls.env["res.partner"].create(
            {
                "name": "Red Butay",
                "family_name": "Butay",
                "given_name": "Red",
                "addl_name": "Red",
                "is_group": False,
                "is_registrant": True,
                "phone": "+639266716912",
            }
        )

        cls.reg_id = cls.env["g2p.reg.id"].create(
            {
                "partner_id": cls.individual_id.id,
                "id_type": cls.id_type_id.id,
                "value": "1234567890",
            }
        )

    def test_get_dci_individual_registry_data(self):
        reg_records = self.individual_id.get_dci_individual_registry_data()
        reg_records_2 = self.individual_2_id.get_dci_individual_registry_data()
        self.assertEqual(len(reg_records), 1)
        self.assertEqual(len(reg_records_2), 0)
        self.assertEqual(reg_records[0]["identifier"][0]["name"], "National ID")
        self.assertEqual(reg_records[0]["identifier"][0]["identifier"], "1234567890")
        self.assertEqual(reg_records[0]["birthDate"], "False")
        self.assertEqual(reg_records[0]["givenName"], "Chin")
        self.assertEqual(reg_records[0]["familyName"], "Franco")
