import logging
from os import path

from odoo import fields
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)

PATH = path.join(path.dirname(__file__), "import_data", "%s.xlsx")
OPTIONS = {
    "headers": True,
    "quoting": '"',
    "separator": ",",
}


class EventPhoneSurveyTest(TransactionCase):
    def setUp(self):
        super().setUp()

        self._test_group = self.env["res.partner"].create(
            {
                "name": "BARASA",
                "is_registrant": True,
                "is_group": True,
            }
        )
        self._test_individual = self.env["res.partner"].create(
            {
                "name": "NJERI, WAMBUI",
                "family_name": "Njeri",
                "given_name": "Wambui",
                "is_group": False,
                "is_registrant": True,
                "phone": "+639266716911",
            }
        )

    def create_event_data(self):
        event_vals = {
            "summary": "Phone Survey",
            "description": "Phone Survey Event Data",
        }
        event = self.env["spp.event.phone.survey"].create(event_vals)
        event_data_vals = {
            "model": "spp.event.phone.survey",
            "partner_id": self._test_individual.id,
            "collection_date": fields.date.today() or False,
            "expiry_date": False,
            "res_id": event.id,
        }
        event_data = self.env["spp.event.data"].create(event_data_vals)

        return event_data

    def create_import_event_data(self, filename, model):
        with open(PATH % filename) as demo_file:
            _logger.info("DEMO FILE: %s", demo_file.read())
            return self.env["spp.event.data.import"].create(
                {
                    "excel_file": demo_file.read(),
                    "name": "%s.csv" % filename,
                    "event_data_model": model,
                }
            )

    def test_01_check_active_house_visit(self):
        event_data = self.create_event_data()
        self._test_individual._compute_active_phone_survey()

        self.assertEqual(
            self._test_individual.active_phone_survey.id,
            event_data.id,
        )

    def test_02_import_and_save(self):
        import_data = self.create_import_event_data(
            "phone_survey", "spp.event.phone.survey"
        )
        import_data.import_data()
        import_data.save_to_event_data()

        self.assertEqual(
            len(self._test_individual.event_data_ids),
            1,
        )
