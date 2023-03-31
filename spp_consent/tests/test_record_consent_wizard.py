from odoo import fields
from odoo.exceptions import UserError

from .common import Common


class TestRecordConsentWiz(Common):
    def test_01_record_consent_raise_error(self):
        test_consent = self._model.create({"group_id": self._test_group.id})
        with self.assertRaisesRegex(UserError, "^.*no selected Signatory.*$"):
            test_consent.record_consent()

    def test_02_record_consent(self):
        self.assertFalse(
            bool(self._test_group.consent_ids.ids),
            "Test group should not having related consent records!",
        )
        test_consent_group = self._model.create(
            {
                "group_id": self._test_group.id,
                "signatory_id": self._test_individual_1.id,
                "config_id": self.env.ref("spp_consent.default_consent_config").id,
                "is_group": True,
                "expiry": fields.Date.today(),
            }
        )
        test_consent_group.record_consent()
        self.assertTrue(
            bool(self._test_group.consent_ids.ids),
            "Test group should now having related consent records!",
        )
        self.assertFalse(
            bool(self._test_individual_1.consent_ids.ids),
            "Test individual should not having related consent records!",
        )
        test_consent_individual = self._model.create(
            {
                "signatory_id": self._test_individual_1.id,
                "config_id": self.env.ref("spp_consent.default_consent_config").id,
                "expiry": fields.Date.today(),
            }
        )
        test_consent_individual.record_consent()
        self.assertTrue(
            bool(self._test_individual_1.consent_ids.ids),
            "Test individual should now having related consent records!",
        )

    def test_03_compute_name(self):
        test_consent = self._model.create(
            {"signatory_id": self._test_individual_1.id, "expiry": fields.Date.today()}
        )
        self.assertEqual(
            test_consent.name,
            "Tywin Lannister",
            "Consent Wizard should have same name with its signatory!",
        )
        test_consent.write(
            {"config_id": self.env.ref("spp_consent.default_consent_config").id}
        )
        self.assertEqual(
            test_consent.name,
            "Default-Tywin Lannister",
            "Consent Wizard should change name!",
        )
