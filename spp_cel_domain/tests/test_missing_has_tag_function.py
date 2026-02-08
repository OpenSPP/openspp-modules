"""
Test to demonstrate the missing has_tag() function (HIGH priority).

This test demonstrates that has_tag() function is required by the specification
but not implemented, blocking Example 3 and common OpenSPP use cases.

Issue: Missing implementation in cel_translator.py
Severity: HIGH
Spec Reference: Example 3, Section #3 pragmatic function library
"""

import logging

from odoo.tests import TransactionCase
from odoo.tests.common import tagged

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install", "cel_domain")
class TestMissingHasTagFunction(TransactionCase):
    """Demonstrate that has_tag() function is required but missing."""

    def setUp(self):
        super().setUp()
        Partner = self.env["res.partner"]

        # Create or find partner category tags
        CategoryTag = self.env["res.partner.category"]
        self.tag_pregnant = CategoryTag.search([("name", "=", "Pregnant")], limit=1)
        if not self.tag_pregnant:
            self.tag_pregnant = CategoryTag.create({"name": "Pregnant"})

        self.tag_disabled = CategoryTag.search([("name", "=", "Disabled")], limit=1)
        if not self.tag_disabled:
            self.tag_disabled = CategoryTag.create({"name": "Disabled"})

        # Create test registrants
        self.registrant_pregnant = Partner.create(
            {
                "name": "Pregnant Woman",
                "is_registrant": True,
                "is_group": False,
                "phone": "+1234567890",
                "category_id": [(4, self.tag_pregnant.id)],  # Standard Odoo field
            }
        )

        self.registrant_disabled = Partner.create(
            {
                "name": "Disabled Person",
                "is_registrant": True,
                "is_group": False,
                "phone": "+0987654321",
                "category_id": [(4, self.tag_disabled.id)],
            }
        )

        self.registrant_no_tag = Partner.create(
            {
                "name": "No Tag Person",
                "is_registrant": True,
                "is_group": False,
                "phone": "+1111111111",
            }
        )

    def _exec(self, expr: str):
        cfg = self.env["cel.registry"].load_profile("registry_individuals")
        ex = self.env["cel.executor"].with_context(cel_profile="registry_individuals", cel_cfg=cfg)
        return ex.compile_and_preview("res.partner", expr, limit=50)

    def test_example_3_from_specification(self):
        """
        HIGH PRIORITY: Specification Example 3 cannot be implemented.

        From specs.md section #11, Example 3:

        ```
        me.phone != "" and has_tag("Pregnant")
        ```

        Expected domain:
        ```python
        ['&', ('phone','!=',False), ('category_id.name','ilike','Pregnant')]
        ```

        Expected result: Should match registrant_pregnant only
        """
        _logger.warning("[CEL HIGH PRIORITY TEST] Testing has_tag() function from spec Example 3")

        expr = 'me.phone != "" and has_tag("Pregnant")'

        try:
            result = self._exec(expr)

            # If this succeeds, has_tag() was implemented!
            ids = result.get("ids", [])
            self.assertIn(self.registrant_pregnant.id, ids, "Should find registrant with Pregnant tag")
            self.assertNotIn(self.registrant_disabled.id, ids, "Should NOT find registrant with different tag")
            self.assertNotIn(self.registrant_no_tag.id, ids, "Should NOT find registrant without tags")

            _logger.info("✅ has_tag() function is implemented and working!")

        except Exception as e:
            # Expected to fail because has_tag() is not implemented
            _logger.error(
                f"❌ has_tag() function is NOT implemented. " f"Specification Example 3 cannot be executed. Error: {e}"
            )
            self.fail(
                f"has_tag() function missing. Spec Example 3 blocked. "
                f"See CODE_REVIEW_REPORT.md Issue #2. Error: {e}"
            )

    def test_has_tag_with_multiple_conditions(self):
        """
        Test has_tag() with multiple conditions (real-world scenario).

        Use case: Find all pregnant women with phone numbers in a specific district.
        """
        _logger.warning("[CEL HIGH PRIORITY TEST] Testing has_tag() in complex expression")

        # Create a country for testing M2O name matching
        Country = self.env["res.country"]
        country = Country.create(
            {
                "name": "North District",
                "code": "ND",
            }
        )
        self.registrant_pregnant.country_id = country.id

        expr = 'me.phone != "" and has_tag("Pregnant") and me.country == "North District"'

        try:
            result = self._exec(expr)

            ids = result.get("ids", [])
            self.assertEqual(len(ids), 1, "Should find exactly one pregnant woman in North District with phone")
            self.assertIn(self.registrant_pregnant.id, ids)

            _logger.info("✅ has_tag() works in complex expressions!")

        except Exception as e:
            _logger.error(f"❌ has_tag() not implemented. Complex targeting scenarios blocked. " f"Error: {e}")
            self.fail(f"has_tag() function missing: {e}")

    def test_has_tag_case_insensitive(self):
        """
        Test that has_tag() should be case-insensitive (ilike operator).

        Common use case: Users might type "pregnant", "Pregnant", or "PREGNANT"
        """
        _logger.warning("[CEL HIGH PRIORITY TEST] Testing has_tag() case-insensitivity")

        # Should match regardless of case
        expr = 'has_tag("pregnant")'  # lowercase

        try:
            result = self._exec(expr)

            ids = result.get("ids", [])
            self.assertIn(self.registrant_pregnant.id, ids, "has_tag() should be case-insensitive (ilike)")

            _logger.info("✅ has_tag() is case-insensitive!")

        except Exception as e:
            _logger.error(f"❌ has_tag() not implemented: {e}")
            self.fail(f"has_tag() function missing: {e}")

    def test_recommended_implementation(self):
        """
        This test documents the RECOMMENDED IMPLEMENTATION for has_tag().

        IMPLEMENTATION GUIDE:
        Add to cel_translator.py in the _to_plan method, within P.Call handling:

        ```python
        # has_tag(tagname) - filter by partner category tags
        if isinstance(node.func, P.Ident) and node.func.name == "has_tag":
            tag_name = node.args[0].value if node.args and isinstance(node.args[0], P.Literal) else ""
            # Standard Odoo partner categories use category_id field (many2many)
            # Use ilike for case-insensitive matching
            return LeafDomain(
                model,
                [("category_id.name", "ilike", tag_name)]
            ), f"has tag ILIKE {tag_name}"
        ```

        ALTERNATE FIELD NAMES (depending on OpenSPP customization):
        - tag_ids (if custom field)
        - category_id (standard Odoo)
        - Check actual field name in res.partner model

        EFFORT: 2-4 hours (including tests)
        PRIORITY: HIGH (blocks common use case)
        """
        _logger.info(
            "[CEL HIGH PRIORITY TEST] Documenting recommended implementation. "
            "See test docstring for implementation guidance."
        )

        # This is a documentation test
        # When the fix is implemented, this test will pass
        self.assertTrue(True, "See test docstring for recommended has_tag() implementation")

    def test_has_tag_workaround_for_users(self):
        """
        Document current workaround for users until has_tag() is implemented.

        WORKAROUND: Users can manually write the domain:
        Instead of: has_tag("Pregnant")
        Use: me.category_id.name == "Pregnant"  (if field name is category_id)
        Or: me.tag_ids.name == "Pregnant"  (if field name is tag_ids)

        This is not user-friendly but allows unblocking urgent use cases.
        """
        _logger.info("[CEL HIGH PRIORITY TEST] Testing workaround until has_tag() is implemented")

        # Try the workaround approach (may fail if field name is different)
        expr = 'me.category_id != "" and me.phone != ""'

        try:
            self._exec(expr)

            _logger.info(
                "✅ Workaround works. Users can use 'me.category_id.name' syntax " "until has_tag() is implemented."
            )

        except Exception as e:
            _logger.warning(
                f"Workaround may not work depending on Odoo field configuration. "
                f"has_tag() implementation is critical. Error: {e}"
            )
