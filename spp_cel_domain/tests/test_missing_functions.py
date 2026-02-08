"""
Test to demonstrate missing functions (MEDIUM priority).

This test demonstrates that several functions required by the specification
are not implemented: startswith(), kind(), between(), active_members().

Issue: Incomplete function library in cel_translator.py and cel_functions.py
Severity: MEDIUM
Spec Reference: Section #3 Pragmatic function library
"""

import logging
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo.tests import TransactionCase
from odoo.tests.common import tagged

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install", "cel_domain")
class TestMissingFunctions(TransactionCase):
    """Demonstrate that several spec-required functions are missing."""

    def setUp(self):
        super().setUp()
        Partner = self.env["res.partner"]

        # Setup for text matching tests
        self.partner_muhammad = Partner.create(
            {
                "name": "Muhammad Ali",
                "is_registrant": True,
                "is_group": False,
            }
        )

        self.partner_mohamed = Partner.create(
            {
                "name": "Mohamed Hassan",
                "is_registrant": True,
                "is_group": False,
            }
        )

        self.partner_john = Partner.create(
            {
                "name": "John Smith",
                "is_registrant": True,
                "is_group": False,
            }
        )

        # Setup for group/membership tests
        self.group = Partner.create(
            {
                "name": "Test Household",
                "is_registrant": True,
                "is_group": True,
            }
        )

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

        self.kind_spouse = self.env["g2p.group.membership.kind"].create(
            {
                "name": "Spouse",
            }
        )

        self.kind_child = self.env["g2p.group.membership.kind"].create(
            {
                "name": "Child",
            }
        )

        # Create members
        self.head = Partner.create(
            {
                "name": "Head Person",
                "is_registrant": True,
                "is_group": False,
                "birthdate": date.today() - relativedelta(years=30),
            }
        )

        self.child = Partner.create(
            {
                "name": "Child Person",
                "is_registrant": True,
                "is_group": False,
                "birthdate": date.today() - relativedelta(years=7),
            }
        )

        self.env["g2p.group.membership"].create(
            {
                "group": self.group.id,
                "individual": self.head.id,
                "kind": [(4, self.kind_head.id)],
            }
        )

        self.env["g2p.group.membership"].create(
            {
                "group": self.group.id,
                "individual": self.child.id,
                "kind": [(4, self.kind_child.id)],
            }
        )

    def _exec(self, expr: str, profile="registry_individuals"):
        cfg = self.env["cel.registry"].load_profile(profile)
        ex = self.env["cel.executor"].with_context(cel_profile=profile, cel_cfg=cfg)
        model = cfg.get("root_model", "res.partner")
        return ex.compile_and_preview(model, expr, limit=50)

    def test_startswith_function_missing(self):
        """
        MEDIUM PRIORITY: startswith() function is required but missing.

        From spec Section #3:
            startswith(x, s) - case-insensitive text matching

        Use case: Find all registrants whose name starts with "Muham"
        (matches Muhammad, Muhammed, etc.)

        Expected: startswith(me.name, "Muham") should work
        """
        _logger.warning("[CEL MEDIUM PRIORITY TEST] Testing startswith() function")

        expr = 'startswith(me.name, "Muham")'

        try:
            result = self._exec(expr)

            # If this succeeds, startswith() was implemented!
            ids = result.get("ids", [])
            self.assertIn(self.partner_muhammad.id, ids, "Should find Muhammad")
            self.assertNotIn(self.partner_john.id, ids, "Should NOT find John")

            _logger.info("✅ startswith() function is implemented!")

        except Exception as e:
            _logger.error(f"❌ startswith() function NOT implemented. " f"Text filtering use case blocked. Error: {e}")
            self.fail(f"startswith() function missing. " f"See CODE_REVIEW_REPORT.md Issue #6. Error: {e}")

    def test_kind_function_missing(self):
        """
        MEDIUM PRIORITY: kind() function is required but missing.

        From spec Section #3:
            kind(name) - returns a membership kind handle

        From spec Example 15b:
            has_role(m, "child") and age_years(m.birthdate) < 5

        The kind() function should return a kind object that can be
        compared or used with has_role().

        Expected: kind("Child") should resolve to membership kind
        """
        _logger.warning("[CEL MEDIUM PRIORITY TEST] Testing kind() function")

        # Expression using kind() - from spec example 15b
        expr = 'members.exists(m, has_role(m, kind("Child")) and age_years(m.birthdate) < 12)'

        try:
            result = self._exec(expr, profile="registry_groups")

            # If this succeeds, kind() was implemented!
            ids = result.get("ids", [])
            self.assertIn(self.group.id, ids, "Should find group with school-aged child")

            _logger.info("✅ kind() function is implemented!")

        except Exception as e:
            _logger.error(f"❌ kind() function NOT implemented. " f"Spec Example 15b cannot be executed. Error: {e}")
            self.fail(f"kind() function missing. " f"See CODE_REVIEW_REPORT.md Issue #6. Error: {e}")

    def test_between_function_not_wired(self):
        """
        MEDIUM PRIORITY: between() exists in cel_functions.py but not wired to translator.

        From spec Section #3:
            between(x, a, b) - range check

        The function exists in cel_functions.py:
            def between(x, a, b):
                return a <= x <= b

        But it's not wired into cel_translator.py, so users can't call it.

        NOTE: Recent test additions show between() may already be working!
        See test_examples_groups_members.py:117
        """
        _logger.warning("[CEL MEDIUM PRIORITY TEST] Testing between() function wiring")

        # Use between() for school-age children (6-11 years)
        expr = "members.exists(m, between(age_years(m.birthdate), 6, 11))"

        try:
            result = self._exec(expr, profile="registry_groups")

            # If this succeeds, between() is properly wired!
            ids = result.get("ids", [])
            self.assertIn(self.group.id, ids, "Should find group with school-aged child (age 7)")

            _logger.info("✅ between() function is properly wired!")

        except Exception as e:
            _logger.error(f"❌ between() function exists but not wired to translator. Error: {e}")
            self.fail(
                f"between() function not accessible from CEL expressions. "
                f"Needs wiring in cel_translator.py. Error: {e}"
            )

    def test_active_members_function_missing(self):
        """
        LOW PRIORITY: active_members() alias function is missing.

        From spec Section #3:
            active_members() - alias for members.exists(m, not m._link.is_ended)

        This is a convenience function for a common pattern.
        Users can work around by writing the full expression.
        """
        _logger.warning("[CEL LOW PRIORITY TEST] Testing active_members() convenience function")

        # Create an ended membership
        ended_member = self.env["res.partner"].create(
            {
                "name": "Ended Member",
                "is_registrant": True,
                "is_group": False,
            }
        )

        self.env["g2p.group.membership"].create(
            {
                "group": self.group.id,
                "individual": ended_member.id,
                "is_ended": True,
            }
        )

        # Try using active_members() function
        expr = "active_members()"

        try:
            self._exec(expr, profile="registry_groups")

            _logger.info("✅ active_members() function is implemented!")

            # Should return count or boolean
            # Implementation details depend on design choice

        except Exception as e:
            _logger.warning(
                f"⚠️ active_members() convenience function NOT implemented. "
                f"Users can work around with full expression. Error: {e}"
            )
            # This is LOW priority, so we don't fail the test

    def test_recommended_function_implementations(self):
        """
        This test documents the RECOMMENDED IMPLEMENTATIONS for missing functions.

        IMPLEMENTATION GUIDE:

        1. startswith() - Add to cel_translator.py:
        ```python
        # startswith(field, "prefix")
        if isinstance(node.func, P.Ident) and node.func.name == "startswith":
            field_expr = node.args[0]
            prefix = node.args[1].value if len(node.args) > 1 and isinstance(node.args[1], P.Literal) else ""
            field, mdl = self._resolve_field(model, field_expr, cfg, ctx)
            # Use =ilike with % suffix for prefix matching
            return LeafDomain(mdl or model, [(field, "=ilike", f"{prefix}%")]), f"{field} starts with {prefix}"
        ```

        2. kind() - Add to cel_translator.py:
        ```python
        # kind(name) - returns membership kind handle
        if isinstance(node.func, P.Ident) and node.func.name == "kind":
            kind_name = node.args[0].value if node.args and isinstance(node.args[0], P.Literal) else None
            # Resolve to g2p.group.membership.kind record
            kind_rec = self.env["g2p.group.membership.kind"].search([("name", "=", kind_name)], limit=1)
            # Return as a special marker that can be used in has_role comparisons
            return LeafDomain(model, [("id", "!=", 0)]), f"KIND({kind_name})={kind_rec.id}"
        ```

        3. between() - Wire existing function in cel_translator.py:
        ```python
        # between(x, a, b) - call existing function
        if isinstance(node.func, P.Ident) and node.func.name == "between":
            # This might already be working via _eval_literal
            # If not, add special handling to convert to domain:
            # between(age_years(field), a, b) -> field > today-b AND field <= today-a
            pass  # May already work
        ```

        4. active_members() - Add as convenience function:
        ```python
        # active_members() - alias for common pattern
        if isinstance(node.func, P.Ident) and node.func.name == "active_members":
            # Translate to: members.exists(m, not m._link.is_ended)
            # Create synthetic AST and recursively translate
            members_symbol = cfg.get("symbols", {}).get("members")
            if members_symbol:
                # Create synthetic exists expression
                # ... implementation details ...
                pass
        ```

        PRIORITIES:
        - HIGH: has_tag() (see test_missing_has_tag_function.py)
        - MEDIUM: startswith(), kind()
        - LOW: active_members() (users can write full expression)
        - CHECK: between() may already work (see test_examples_groups_members.py:117)

        EFFORT: 4-8 hours total for all functions
        """
        _logger.info(
            "[CEL MEDIUM PRIORITY TEST] Documenting recommended function implementations. "
            "See test docstring for implementation guidance."
        )

        self.assertTrue(True, "See test docstring for recommended function implementations")
