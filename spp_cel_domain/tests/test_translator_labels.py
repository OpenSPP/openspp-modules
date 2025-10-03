from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install", "cel_domain")
class TestTranslatorLabelFields(TransactionCase):
    def setUp(self):
        super().setUp()
        Gender = self.env["gender.type"]
        self.female = Gender.search([("value", "=", "Female")], limit=1) or Gender.create(
            {"code": "F", "value": "Female"}
        )
        self.male = Gender.search([("value", "=", "Male")], limit=1) or Gender.create({"code": "M", "value": "Male"})
        P = self.env["res.partner"]
        self.pf = P.create({"name": "Alice", "is_registrant": True, "is_group": False, "gender": self.female.id})
        self.pm = P.create({"name": "Bob", "is_registrant": True, "is_group": False, "gender": self.male.id})
        cfg = self.env["cel.registry"].load_profile("registry_individuals")
        # Restrict to the two created records
        cfg = dict(cfg)
        cfg["base_domain"] = [("id", "in", [self.pf.id, self.pm.id])]
        self.exec = self.env["cel.executor"].with_context(cel_profile="registry_individuals", cel_cfg=cfg)

    def test_gender_label_match(self):
        res = self.exec.compile_and_preview("res.partner", 'me.gender == "Female"', limit=0)
        ids = set(res["ids"])
        assert self.pf.id in ids
        assert self.pm.id not in ids
