"""
Integration tests with realistic OpenSPP/OpenG2P scenarios.

Tests complete workflows and realistic use cases:
- Social protection program eligibility
- Household targeting
- Benefit distribution
- Vulnerability assessments
"""

import logging
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo.tests import TransactionCase
from odoo.tests.common import tagged

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install", "cel_domain")
class TestIntegrationScenarios(TransactionCase):
    """Integration tests with realistic OpenSPP scenarios."""

    def setUp(self):
        super().setUp()

        # Set up gender types (many2one field)
        Gender = self.env["gender.type"]
        self.gender_female = Gender.search([("value", "ilike", "female")], limit=1)
        if not self.gender_female:
            self.gender_female = Gender.create({"code": "F", "value": "Female"})

        self.gender_male = Gender.search([("value", "ilike", "male")], limit=1)
        if not self.gender_male:
            self.gender_male = Gender.create({"code": "M", "value": "Male"})

        # Create category tags
        Category = self.env["res.partner.category"]
        self.tag_pregnant = Category.create({"name": "Pregnant"})
        self.tag_disabled = Category.create({"name": "Disabled"})
        self.tag_elderly = Category.create({"name": "Elderly"})

        # Create membership kinds
        try:
            self.kind_head = self.env.ref("g2p_registry_membership.group_membership_kind_head")
        except Exception:
            self.kind_head = self.env["g2p.group.membership.kind"].create(
                {
                    "name": "Head",
                    "is_unique": True,
                }
            )

        self.kind_spouse = self.env["g2p.group.membership.kind"].create({"name": "Spouse"})
        self.kind_child = self.env["g2p.group.membership.kind"].create({"name": "Child"})

        Partner = self.env["res.partner"]
        Membership = self.env["g2p.group.membership"]

        # Scenario 1: Woman-headed household with young children
        self.household_1 = Partner.create(
            {
                "name": "Household 1 (Woman-headed, 2 young children)",
                "is_registrant": True,
                "is_group": True,
            }
        )

        self.mother_1 = Partner.create(
            {
                "name": "Sarah Johnson",
                "is_registrant": True,
                "is_group": False,
                "birthdate": date.today() - relativedelta(years=32),
                "gender": self.gender_female.id,  # ✅ Use .id
                "phone": "+1234567890",
            }
        )

        self.child_1a = Partner.create(
            {
                "name": "Emma Johnson",
                "is_registrant": True,
                "is_group": False,
                "birthdate": date.today() - relativedelta(years=3),
                "gender": self.gender_female.id,
            }
        )

        self.child_1b = Partner.create(
            {
                "name": "Liam Johnson",
                "is_registrant": True,
                "is_group": False,
                "birthdate": date.today() - relativedelta(years=5),
                "gender": self.gender_male.id,
            }
        )

        Membership.create(
            {
                "group": self.household_1.id,
                "individual": self.mother_1.id,
                "kind": [(4, self.kind_head.id)],
                "is_ended": False,
            }
        )

        Membership.create(
            {
                "group": self.household_1.id,
                "individual": self.child_1a.id,
                "kind": [(4, self.kind_child.id)],
                "is_ended": False,
            }
        )

        Membership.create(
            {
                "group": self.household_1.id,
                "individual": self.child_1b.id,
                "kind": [(4, self.kind_child.id)],
                "is_ended": False,
            }
        )

        # Scenario 2: Elderly couple
        self.household_2 = Partner.create(
            {
                "name": "Household 2 (Elderly couple)",
                "is_registrant": True,
                "is_group": True,
            }
        )

        self.elderly_male = Partner.create(
            {
                "name": "Ahmed Hassan",
                "is_registrant": True,
                "is_group": False,
                "birthdate": date.today() - relativedelta(years=68),
                "gender": self.gender_male.id,
                "phone": "+9876543210",
                "category_id": [(6, 0, [self.tag_elderly.id])],
            }
        )

        self.elderly_female = Partner.create(
            {
                "name": "Fatima Hassan",
                "is_registrant": True,
                "is_group": False,
                "birthdate": date.today() - relativedelta(years=65),
                "gender": self.gender_female.id,
                "category_id": [(6, 0, [self.tag_elderly.id])],
            }
        )

        Membership.create(
            {
                "group": self.household_2.id,
                "individual": self.elderly_male.id,
                "kind": [(4, self.kind_head.id)],
                "is_ended": False,
            }
        )

        Membership.create(
            {
                "group": self.household_2.id,
                "individual": self.elderly_female.id,
                "kind": [(4, self.kind_spouse.id)],
                "is_ended": False,
            }
        )

        # Scenario 3: Pregnant woman (individual registrant)
        self.pregnant_woman = Partner.create(
            {
                "name": "Maria Garcia",
                "is_registrant": True,
                "is_group": False,
                "birthdate": date.today() - relativedelta(years=28),
                "gender": self.gender_female.id,
                "phone": "+1122334455",
                "category_id": [(6, 0, [self.tag_pregnant.id])],
            }
        )

        # Scenario 4: School-aged children household
        self.household_3 = Partner.create(
            {
                "name": "Household 3 (School-aged children)",
                "is_registrant": True,
                "is_group": True,
            }
        )

        self.parent_3 = Partner.create(
            {
                "name": "David Smith",
                "is_registrant": True,
                "is_group": False,
                "birthdate": date.today() - relativedelta(years=40),
                "gender": self.gender_male.id,
            }
        )

        self.child_3a = Partner.create(
            {
                "name": "Anna Smith",
                "is_registrant": True,
                "is_group": False,
                "birthdate": date.today() - relativedelta(years=8),
                "gender": self.gender_female.id,
            }
        )

        self.child_3b = Partner.create(
            {
                "name": "Ben Smith",
                "is_registrant": True,
                "is_group": False,
                "birthdate": date.today() - relativedelta(years=10),
                "gender": self.gender_male.id,
            }
        )

        Membership.create(
            {
                "group": self.household_3.id,
                "individual": self.parent_3.id,
                "kind": [(4, self.kind_head.id)],
                "is_ended": False,
            }
        )

        Membership.create(
            {
                "group": self.household_3.id,
                "individual": self.child_3a.id,
                "kind": [(4, self.kind_child.id)],
                "is_ended": False,
            }
        )

        Membership.create(
            {
                "group": self.household_3.id,
                "individual": self.child_3b.id,
                "kind": [(4, self.kind_child.id)],
                "is_ended": False,
            }
        )

    def _exec(self, expr, profile="registry_groups"):
        """Helper to execute CEL expression."""
        registry = self.env["cel.registry"]
        cfg = registry.load_profile(profile)
        executor = self.env["cel.executor"].with_context(cel_profile=profile, cel_cfg=cfg)
        model = cfg.get("root_model", "res.partner")
        return executor.compile_and_preview(model, expr, limit=50)

    def test_scenario_early_childhood_program(self):
        """
        Scenario: Early Childhood Development Program
        Eligibility: Households with children under 5 years old
        """
        _logger.info("[CEL INTEGRATION] Early Childhood Program targeting")

        expr = "members.exists(m, age_years(m.birthdate) < 5)"
        result = self._exec(expr)

        # Should match household_1 (has 2 children under 5)
        self.assertIn(self.household_1.id, result.get("ids", []))

        # Should NOT match household_2 (elderly couple)
        self.assertNotIn(self.household_2.id, result.get("ids", []))

        # Should NOT match household_3 (school-aged children)
        self.assertNotIn(self.household_3.id, result.get("ids", []))

        _logger.info(f"✅ Early Childhood targeting: {result.get('count')} households eligible")

    def test_scenario_single_mother_support(self):
        """
        Scenario: Single Mother Support Program
        Eligibility: Female-headed households with young children
        """
        _logger.info("[CEL INTEGRATION] Single Mother Support targeting")

        expr = (
            "count(members, m, head(m)) == 1 and "
            "members.exists(m, head(m) and m.gender == 'Female') and "
            "members.exists(m, age_years(m.birthdate) < 5)"
        )
        result = self._exec(expr)

        # Should match household_1 (female head with young children)
        self.assertIn(self.household_1.id, result.get("ids", []))

        _logger.info(f"✅ Single Mother targeting: {result.get('count')} households eligible")

    def test_scenario_elderly_pension_program(self):
        """
        Scenario: Elderly Pension Program
        Eligibility: Individuals 60+ years old
        """
        _logger.info("[CEL INTEGRATION] Elderly Pension targeting")

        expr = "age_years(me.birthdate) >= 60"
        result = self._exec(expr, profile="registry_individuals")

        # Should match elderly couple
        self.assertIn(self.elderly_male.id, result.get("ids", []))
        self.assertIn(self.elderly_female.id, result.get("ids", []))

        # Should NOT match younger individuals
        self.assertNotIn(self.mother_1.id, result.get("ids", []))
        self.assertNotIn(self.pregnant_woman.id, result.get("ids", []))

        _logger.info(f"✅ Elderly Pension targeting: {result.get('count')} individuals eligible")

    def test_scenario_elderly_household_with_phone(self):
        """
        Scenario: Elderly Pension with Phone Verification
        Eligibility: Households with elderly members AND phone number
        """
        _logger.info("[CEL INTEGRATION] Elderly with Phone targeting")

        expr = "members.exists(m, age_years(m.birthdate) >= 60) and " "members.exists(m, m.phone != '')"
        result = self._exec(expr)

        # Should match household_2 (elderly couple with phone)
        self.assertIn(self.household_2.id, result.get("ids", []))

        _logger.info(f"✅ Elderly with Phone targeting: {result.get('count')} households eligible")

    def test_scenario_maternal_health_program(self):
        """
        Scenario: Maternal Health Program
        Eligibility: Pregnant women with phone numbers
        """
        _logger.info("[CEL INTEGRATION] Maternal Health targeting")

        expr = "has_tag('Pregnant') and me.phone != ''"
        result = self._exec(expr, profile="registry_individuals")

        # Should match pregnant woman
        self.assertIn(self.pregnant_woman.id, result.get("ids", []))

        _logger.info(f"✅ Maternal Health targeting: {result.get('count')} individuals eligible")

    def test_scenario_school_feeding_program(self):
        """
        Scenario: School Feeding Program
        Eligibility: Households with children aged 6-11 years
        """
        _logger.info("[CEL INTEGRATION] School Feeding targeting")

        expr = "members.exists(m, between(age_years(m.birthdate), 6, 11))"
        result = self._exec(expr)

        # Should match household_3 (has children aged 8 and 10)
        self.assertIn(self.household_3.id, result.get("ids", []))

        # Should NOT match household_1 (children under 6)
        self.assertNotIn(self.household_1.id, result.get("ids", []))

        _logger.info(f"✅ School Feeding targeting: {result.get('count')} households eligible")

    def test_scenario_combined_age_and_tag_filter(self):
        """
        Scenario: Combined filters
        Eligibility: Elderly individuals (60+) tagged as "Elderly"
        """
        _logger.info("[CEL INTEGRATION] Combined age and tag targeting")

        expr = "age_years(me.birthdate) >= 60 and has_tag('Elderly')"
        result = self._exec(expr, profile="registry_individuals")

        # Should match elderly couple (both tagged)
        self.assertIn(self.elderly_male.id, result.get("ids", []))
        self.assertIn(self.elderly_female.id, result.get("ids", []))

        _logger.info(f"✅ Combined filter targeting: {result.get('count')} individuals eligible")

    def test_scenario_name_search_multilingual(self):
        """
        Scenario: Name-based search (multilingual support)
        Use case: Find individuals whose names start with specific patterns
        """
        _logger.info("[CEL INTEGRATION] Name search targeting")

        # Search for names starting with "Maria"
        expr = 'startswith(me.name, "Maria")'
        result = self._exec(expr, profile="registry_individuals")

        # Should match pregnant woman (Maria Garcia)
        self.assertIn(self.pregnant_woman.id, result.get("ids", []))

        _logger.info(f"✅ Name search targeting: {result.get('count')} individuals found")
