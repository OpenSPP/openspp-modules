from odoo.tests.common import TransactionCase


class IdDetailsIndividualTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """
        Setup and create necessary records for this test
        """
        super().setUpClass()

        cls.applicant = cls.env["res.partner"].create(
            {
                "name": "Chin Franco",
                "family_name": "Franco",
                "given_name": "Chin",
                "is_group": False,
                "is_registrant": True,
                "phone": "+639266716911",
            }
        )

    def test_on_scan_id_document_details_success(self):
        self.applicant.id_document_details = """{
            "photo": "",
            "given_name": "Blue",
            "family_name": "Red",
            "birth_date": "1970-06-18",
            "gender": "Male",
            "document_type": "Passport",
            "document_number": "162401579884",
            "expiry_date": "06/18/2025",
            "nationality": "Philippines",
            "birth_place_city": "Caloocan"
        }"""

        self.applicant.on_scan_id_document_details()

        self.assertEqual(self.applicant.family_name, "Red")
        self.assertEqual(self.applicant.given_name, "Blue")
        self.assertEqual(self.applicant.gender, "Male")

    def test_scan_id_document_details_vals(self):
        details = {
            "photo": "",
            "given_name": "Blue",
            "family_name": "Red",
            "birth_date": "1970-06-18",
            "gender": "Male",
            "document_type": "Passport",
            "document_number": "162401579884",
            "expiry_date": "06/18/2025",
            "nationality": "Philippines",
            "birth_place_city": "Caloocan",
        }

        vals = self.applicant.scan_id_document_details_vals(details)

        self.assertEqual(
            [
                details["family_name"],
                details["given_name"],
                details["birth_date"],
                details["gender"],
                details["birth_place_city"],
            ],
            [
                vals.get("family_name"),
                vals.get("given_name"),
                vals.get("birthdate"),
                vals.get("gender"),
                vals.get("birth_place"),
            ],
        )
