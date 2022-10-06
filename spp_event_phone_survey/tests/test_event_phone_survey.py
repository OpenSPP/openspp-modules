import logging

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class EventPhoneSurveyTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(EventPhoneSurveyTest, cls).setUpClass()

        # Initial Setup of Variables
        cls.group_1 = cls.env["res.partner"].create(
            {
                "name": "Group 1",
                "is_registrant": True,
                "is_group": True,
            }
        )
        cls.phone_survey_1 = cls.env["spp.event.phone.survey"].create(
            {
                "registrant": cls.group_1.id,
                "summary": "Testing Visit",
                "description": "This visit is for testing only",
            }
        )

    def test_01_check_active_phone_survey(self):
        self.group_1._compute_active_phone_survey()
        event_id = self.env["spp.event.data"].search(
            [
                ("model", "=", "spp.event.phone.survey"),
                ("res_id", "=", self.phone_survey_1.id),
            ]
        )
        self.assertEqual(
            self.group_1.active_phone_survey.id,
            event_id.id,
        )

    def test_02_check_name(self):
        self.assertEqual(
            self.group_1.active_phone_survey.name,
            "Phone Survey - [Testing Visit]",
        )

    def test_03_recheck_active_phone_survey_after_entering_new_visit(self):
        if self.group_1.active_phone_survey:
            self.group_1.end_active_event(self.group_1.active_phone_survey)

        vals = {
            "registrant": self.group_1.id,
            "summary": "Testing Visit 2",
            "description": "This visit is for testing again",
        }
        phone_survey_2 = self.env["spp.event.phone.survey"].create(vals)

        self.group_1._compute_active_phone_survey()
        event_id = self.env["spp.event.data"].search(
            [
                ("model", "=", "spp.event.phone.survey"),
                ("res_id", "=", phone_survey_2.id),
            ]
        )
        self.assertEqual(
            self.group_1.active_phone_survey.id,
            event_id.id,
        )
