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
                "addl_name": "Chin",
                "is_group": False,
                "is_registrant": True,
                "phone": "+639266716911",
            }
        )

    def test_on_scan_id_document_details_success(self):
        self.applicant.id_document_details = (
            "{"
            '"photo": "",'
            '"given_name": "Blue",'
            '"family_name": "Red",'
            '"birth_date": "1970-06-18",'
            '"document_type": "Passport",'
            '"document_number": "162401579884",'
            '"expiry_date": "06/18/2025",'
            '"nationality": "Philippines",'
            '"birth_place_city": "Caloocan",'
            '"image": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlz'
            "AAAApgAAAKYB3X3/OAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANCSURBVEiJtZZPbBtFFMZ/M7ubXdtdb1xSFyeilBapySVU8h8OoFaooFSqiihIVIpQBKci6KEg9Q6H9"
            "kovIHoCIVQJJCKE1ENFjnAgcaSGC6rEnxBwA04Tx43t2FnvDAfjkNibxgHxnWb2e/u992bee7tCa00YFsffekFY+nUzFtjW0LrvjRXrCDIAaPLlW0nHL0SsZtVoaF98mLrx3pdhOqLtYPHChahZcYYO7"
            "KvPFxvRl5XPp1sN3adWiD1ZAqD6XYK1b/dvE5IWryTt2udLFedwc1+9kLp+vbbpoDh+6TklxBeAi9TL0taeWpdmZzQDry0AcO+jQ12RyohqqoYoo8RDwJrU+qXkjWtfi8Xxt58BdQuwQs9qC/afLwCw8"
            "tnQbqYAPsgxE1S6F3EAIXux2oQFKm0ihMsOF71dHYx+f3NND68ghCu1YIoePPQN1pGRABkJ6Bus96CutRZMydTl+TvuiRW1m3n0eDl0vRPcEysqdXn+jsQPsrHMquGeXEaY4Yk4wxWcY5V/9scqOMOVU"
            "FthatyTy8QyqwZ+kDURKoMWxNKr2EeqVKcTNOajqKoBgOE28U4tdQl5p5bwCw7BWquaZSzAPlwjlithJtp3pTImSqQRrb2Z8PHGigD4RZuNX6JYj6wj7O4TFLbCO/Mn/m8R+h6rYSUb3ekokRY6f/Yuk"
            "ArN979jcW+V/S8g0eT/N3VN3kTqWbQ428m9/8k0P/1aIhF36PccEl6EhOcAUCrXKZXXWS3XKd2vc/TRBG9O5ELC17MmWubD2nKhUKZa26Ba2+D3P+4/MNCFwg59oWVeYhkzgN/JDR8deKBoD7Y+ljEjGZ"
            "0sosXVTvbc6RHirr2reNy1OXd6pJsQ+gqjk8VWFYmHrwBzW/n+uMPFiRwHB2I7ih8ciHFxIkd/3Omk5tCDV1t+2nNu5sxxpDFNx+huNhVT3/zMDz8usXC3ddaHBj1GHj/As08fwTS7Kt1HBTmyN29vdwAw"
            '+/wbwLVOJ3uAD1wi/dUH7Qei66PfyuRj4Ik9is+hglfbkbfR3cnZm7chlUWLdwmprtCohX4HUtlOcQjLYCu+fzGJH2QRKvP3UNz8bWk1qMxjGTOMThZ3kvgLI5AzFfo379UAAAAASUVORK5CYII="'
            "}"
        )

        self.applicant.on_scan_id_document_details()

        self.assertEqual(self.applicant.family_name, "Red")
        self.assertEqual(self.applicant.given_name, "Blue")

    def test_on_scan_id_document_details_failure(self):
        # Invalid JSON
        self.applicant.id_document_details = """{
            "photo": "",
            "given_name": "Blue",
            "family_name": "Red",
            "birth_date": "1970-06-18",
            "document_type": "Passport",
            "document_number": "162401579884",
            "expiry_date": "06/18/2025",
            "nationality": "Philippines",
            "birth_place_city": "Caloocan",
        }"""
        self.applicant.on_scan_id_document_details()

        self.assertEqual(self.applicant.family_name, "Franco")
        self.assertEqual(self.applicant.given_name, "Chin")
        self.assertEqual(self.applicant.id_document_details, "")

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
