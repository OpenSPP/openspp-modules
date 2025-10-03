import logging
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo.tests import TransactionCase
from odoo.tests.common import tagged

_logger = logging.getLogger("odoo.addons.spp_cel_domain")


@tagged("post_install", "-at_install", "cel_domain")
class TestExamplesGroups(TransactionCase):
    def setUp(self):
        super().setUp()
        # Ensure gender types exist
        Gender = self.env["gender.type"]
        self.gender_female = Gender.search([("value", "ilike", "female")], limit=1)
        if not self.gender_female:
            self.gender_female = Gender.create({"code": "F", "value": "Female"})
        self.gender_male = Gender.search([("value", "ilike", "male")], limit=1)
        if not self.gender_male:
            self.gender_male = Gender.create({"code": "M", "value": "Male"})

        # Load Head-of-Household kind
        try:
            self.kind_head = self.env.ref("g2p_registry_membership.group_membership_kind_head")
        except Exception:
            self.kind_head = self.env["g2p.group.membership.kind"].create({"name": "Head", "is_unique": True})

        # HH1: single head (female 65), one child (age 3)
        Partner = self.env["res.partner"]
        self.hh1 = Partner.create({"name": "HH1", "is_registrant": True, "is_group": True})
        self.hh2 = Partner.create({"name": "HH2", "is_registrant": True, "is_group": True})
        self.hh3 = Partner.create({"name": "HH3", "is_registrant": True, "is_group": True})

        self.head_f65 = Partner.create(
            {
                "name": "Head F65",
                "is_registrant": True,
                "is_group": False,
                "birthdate": date.today() - relativedelta(years=65),
                "gender": self.gender_female.id,
            }
        )
        self.child_3 = Partner.create(
            {
                "name": "Child 3",
                "is_registrant": True,
                "is_group": False,
                "birthdate": date.today() - relativedelta(years=3),
                "gender": self.gender_male.id,
            }
        )
        self.env["g2p.group.membership"].create(
            {"group": self.hh1.id, "individual": self.head_f65.id, "kind": [(4, self.kind_head.id)]}
        )
        self.env["g2p.group.membership"].create({"group": self.hh1.id, "individual": self.child_3.id})

        # HH2: two heads (violates single head)
        head2 = Partner.create(
            {
                "name": "Head2",
                "is_registrant": True,
                "is_group": False,
                "birthdate": date.today() - relativedelta(years=40),
                "gender": self.gender_male.id,
            }
        )
        self.env["g2p.group.membership"].create(
            {"group": self.hh2.id, "individual": self.head_f65.id, "kind": [(4, self.kind_head.id)]}
        )
        self.env["g2p.group.membership"].create(
            {"group": self.hh2.id, "individual": head2.id, "kind": [(4, self.kind_head.id)]}
        )

        # HH3: only male member, no female
        self.env["g2p.group.membership"].create({"group": self.hh3.id, "individual": head2.id})

        # HH4: single head (female 30), two children under 5
        self.hh4 = Partner.create({"name": "HH4", "is_registrant": True, "is_group": True})
        self.head_f30 = Partner.create(
            {
                "name": "Head F30",
                "is_registrant": True,
                "is_group": False,
                "birthdate": date.today() - relativedelta(years=30),
                "gender": self.gender_female.id,
            }
        )
        self.kid_2 = Partner.create(
            {
                "name": "Kid 2",
                "is_registrant": True,
                "is_group": False,
                "birthdate": date.today() - relativedelta(years=2),
                "gender": self.gender_male.id,
            }
        )
        self.kid_4 = Partner.create(
            {
                "name": "Kid 4",
                "is_registrant": True,
                "is_group": False,
                "birthdate": date.today() - relativedelta(years=4),
                "gender": self.gender_female.id,
            }
        )
        self.env["g2p.group.membership"].create(
            {"group": self.hh4.id, "individual": self.head_f30.id, "kind": [(4, self.kind_head.id)]}
        )
        self.env["g2p.group.membership"].create({"group": self.hh4.id, "individual": self.kid_2.id})
        self.env["g2p.group.membership"].create({"group": self.hh4.id, "individual": self.kid_4.id})

        # HH5: school-aged child 7
        self.hh5 = Partner.create({"name": "HH5", "is_registrant": True, "is_group": True})
        self.child_7 = Partner.create(
            {
                "name": "Child 7",
                "is_registrant": True,
                "is_group": False,
                "birthdate": date.today() - relativedelta(years=7),
                "gender": self.gender_male.id,
            }
        )
        self.env["g2p.group.membership"].create(
            {"group": self.hh5.id, "individual": self.head_f65.id, "kind": [(4, self.kind_head.id)]}
        )
        self.env["g2p.group.membership"].create({"group": self.hh5.id, "individual": self.child_7.id})

        # HH6: elderly male head 65
        self.hh6 = Partner.create({"name": "HH6", "is_registrant": True, "is_group": True})
        self.head_m65 = Partner.create(
            {
                "name": "Head M65",
                "is_registrant": True,
                "is_group": False,
                "birthdate": date.today() - relativedelta(years=65),
                "gender": self.gender_male.id,
            }
        )
        self.env["g2p.group.membership"].create(
            {"group": self.hh6.id, "individual": self.head_m65.id, "kind": [(4, self.kind_head.id)]}
        )

    def _exec(self, expr: str):
        cfg = self.env["cel.registry"].load_profile("registry_groups")
        ex = self.env["cel.executor"].with_context(cel_profile="registry_groups", cel_cfg=cfg)
        return ex.compile_and_preview("res.partner", expr, limit=50)

    def test_single_head_child_under5(self):
        _logger.info("[CEL TEST] Running test_single_head_child_under5")
        expr = (
            "count(members, m, head(m) and not m._link.is_ended) == 1 "
            "and members.exists(m, age_years(m.birthdate) < 5 and not m._link.is_ended)"
        )
        res = self._exec(expr)
        self.assertIn(self.hh1.id, res["ids"])  # matches HH1
        self.assertNotIn(self.hh2.id, res["ids"])  # HH2 violates single-head
        _logger.info("CELTEST: TestExamplesGroups.test_single_head_child_under5 PASS")

    def test_elderly_woman_headed(self):
        _logger.info("[CEL TEST] Running test_elderly_woman_headed")
        expr = (
            'members.exists(m, head(m) and m.gender == "Female" '
            "and age_years(m.birthdate) >= 60 and not m._link.is_ended)"
        )
        res = self._exec(expr)
        self.assertIn(self.hh1.id, res["ids"])  # HH1 has elderly female head
        # Predicate female-only should not match HH3
        res2 = self._exec('members.exists(m, m.gender == "Female")')
        self.assertNotIn(self.hh3.id, res2["ids"])  # HH3 all male
        _logger.info("CELTEST: TestExamplesGroups.test_elderly_woman_headed PASS")

    def test_single_head_two_children_under5(self):
        _logger.info("[CEL TEST] Running test_single_head_two_children_under5")
        expr = (
            "count(members, m, head(m) and not m._link.is_ended) == 1 "
            "and count(members, m, age_years(m.birthdate) < 5 and not m._link.is_ended) >= 2"
        )
        res = self._exec(expr)
        self.assertIn(self.hh4.id, res["ids"])  # HH4 has two children under 5
        self.assertNotIn(self.hh2.id, res["ids"])  # HH2 has two heads
        _logger.info("CELTEST: TestExamplesGroups.test_single_head_two_children_under5 PASS")

    def test_school_aged_child_exists(self):
        _logger.info("[CEL TEST] Running test_school_aged_child_exists")
        expr = "members.exists(m, between(age_years(m.birthdate), 6, 11) and not m._link.is_ended)"
        res = self._exec(expr)
        self.assertIn(self.hh5.id, res["ids"])  # HH5 has child age 7
        _logger.info("CELTEST: TestExamplesGroups.test_school_aged_child_exists PASS")

    def test_elderly_male_headed(self):
        _logger.info("[CEL TEST] Running test_elderly_male_headed")
        expr = (
            'members.exists(m, head(m) and m.gender == "Male" '
            "and age_years(m.birthdate) >= 60 and not m._link.is_ended)"
        )
        res = self._exec(expr)
        self.assertIn(self.hh6.id, res["ids"])  # HH6 has elderly male head
        _logger.info("CELTEST: TestExamplesGroups.test_elderly_male_headed PASS")
