from odoo.tests import TransactionCase


class TestCelTranslator(TransactionCase):
    def test_translate_age(self):
        tr = self.env["cel.translator"]
        cfg = self.env["cel.registry"].load_profile("registry_groups")
        plan, explain = tr.translate("res.partner", "members.exists(m, age_years(m.birthdate) < 5)", cfg)
        self.assertTrue(plan)
        self.assertIn("EXISTS", explain)

    def test_translate_enrollment_exists(self):
        tr = self.env["cel.translator"]
        cfg = self.env["cel.registry"].load_profile("registry_individuals")
        plan, explain = tr.translate("res.partner", 'exists(enrollments, e, e.state == "enrolled")', cfg)
        self.assertTrue(plan)
        self.assertIn("EXISTS", explain)

    def test_translate_entitlement_exists(self):
        tr = self.env["cel.translator"]
        cfg = self.env["cel.registry"].load_profile("registry_individuals")
        plan, explain = tr.translate("res.partner", 'exists(entitlements, t, t.state == "approved")', cfg)
        self.assertTrue(plan)
        self.assertIn("EXISTS", explain)
