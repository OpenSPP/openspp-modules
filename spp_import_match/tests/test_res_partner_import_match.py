import logging
from os import path

from odoo.tests import TransactionCase

_logger = logging.getLogger(__name__)

PATH = path.join(path.dirname(__file__), "import_data", "%s.csv")
OPTIONS = {
    "headers": True,
    "quoting": '"',
    "separator": ",",
}


class TestResPartnerImportMatch(TransactionCase):
    def setUp(self):
        super().setUp()
        self._test_hh = self.env["res.partner"].create(
            {
                "name": "Renaud",
                "is_registrant": True,
                "is_group": True,
                "email": "renaud@gmail.com",
            }
        )
        self._test_applicant = self.env["res.partner"].create(
            {
                "name": "Rufino Renaud",
                "family_name": "Rufino",
                "given_name": "Renaud",
                "is_group": False,
                "is_registrant": True,
                "phone": "+639266716911",
                "email": "rufinorenaud12@gmail.com",
            }
        )

    def _base_import_record(self, res_model, file_name):
        with open(PATH % file_name) as demo_file:
            return self.env["base_import.import"].create(
                {
                    "res_model": res_model,
                    "file": demo_file.read(),
                    "file_name": "%s.csv" % file_name,
                    "file_type": "csv",
                }
            )

    def create_matching_given_family_name(self):
        res_partner = self.env["ir.model"].search([("model", "=", "res.partner")])
        vals = {"model_id": res_partner.id}
        import_match = self.env["spp.import.match"].create(vals)
        given_name_field = self.env["ir.model.fields"].search(
            [("name", "=", "given_name"), ("model_id", "=", res_partner.id)]
        )

        self.env["spp.import.match.fields"].create({"field_id": given_name_field.id, "match_id": import_match.id})

        family_name_field = self.env["ir.model.fields"].search(
            [("name", "=", "family_name"), ("model_id", "=", res_partner.id)]
        )

        self.env["spp.import.match.fields"].create({"field_id": family_name_field.id, "match_id": import_match.id})

        return import_match

    def create_matching_name(self):
        res_partner = self.env["ir.model"].search([("model", "=", "res.partner")])
        vals = {"model_id": res_partner.id}
        import_match = self.env["spp.import.match"].create(vals)
        name_field = self.env["ir.model.fields"].search([("name", "=", "name"), ("model_id", "=", res_partner.id)])

        self.env["spp.import.match.fields"].create({"field_id": name_field.id, "match_id": import_match.id})

        return import_match

    # Failing Tests
    # TODO: Fix these test cases
    # def test_01_res_partner_change_email_by_name(self):
    #     """Change email based on given_name, family_name."""
    #     self.create_matching_given_family_name()
    #     record = self._base_import_record("res.partner", "res_partner_name")

    #     record.execute_import(["given_name", "family_name", "name", "email"], [], OPTIONS)

    #     self._test_applicant.env.cache.invalidate()
    #     self.assertEqual(self._test_applicant.email, "rufinorenaud@gmail.com")

    # def test_02_res_partner_change_email_by_group_name(self):
    #     """Change email based on name."""
    #     self.create_matching_name()
    #     record = self._base_import_record("res.partner", "res_partner_group_name")

    #     record.execute_import(["name", "email"], [], OPTIONS)

    #     self._test_hh.env.cache.invalidate()
    #     self.assertEqual(self._test_hh.email, "renaudhh@gmail.com")
