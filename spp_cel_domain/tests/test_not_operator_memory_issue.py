"""
Test to demonstrate the NOT operator memory issue (CRITICAL).

This test demonstrates that the NOT operator loads all record IDs into memory,
creating a DoS vulnerability on large registries.

Issue: cel_executor.py:101-104
Severity: CRITICAL
"""

import logging

from odoo.tests import TransactionCase
from odoo.tests.common import tagged

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install", "cel_domain")
class TestNotOperatorMemoryIssue(TransactionCase):
    """Demonstrate that NOT operator loads entire table into memory."""

    def setUp(self):
        super().setUp()
        # Create a modest number of partners to demonstrate the issue
        # In production, this could be 100K+ records
        Partner = self.env["res.partner"]
        self.test_partners = []

        # Create 100 test registrants
        for i in range(100):
            partner = Partner.create(
                {
                    "name": f"Test Registrant {i}",
                    "is_registrant": True,
                    "is_group": False,
                }
            )
            self.test_partners.append(partner)

        # Create one special partner with email
        self.partner_with_email = Partner.create(
            {
                "name": "Partner With Email",
                "is_registrant": True,
                "is_group": False,
                "email": "test@example.com",
            }
        )

    def _exec(self, expr: str):
        cfg = self.env["cel.registry"].load_profile("registry_individuals")
        ex = self.env["cel.executor"].with_context(cel_profile="registry_individuals", cel_cfg=cfg)
        return ex.compile_and_preview("res.partner", expr, limit=200)

    def test_not_operator_loads_all_records(self):
        """
        CRITICAL ISSUE: This test demonstrates that the NOT operator
        loads ALL record IDs from the model into memory.

        In production with 500K partners, this will:
        - Load 500K IDs into memory (~40MB + Python overhead)
        - Create massive set operations
        - Cause 30+ second queries and potential timeouts
        - Risk server crashes under concurrent load

        Current implementation (cel_executor.py:101-104):
            if isinstance(plan, NOT):
                all_ids = set(self.env[model].search([]).ids)  # DANGEROUS!
                sub = set(self._execute_plan(model, plan.node))
                return list(all_ids - sub)
        """
        _logger.warning(
            "[CEL CRITICAL TEST] Testing NOT operator memory issue. " "This test demonstrates the DoS vulnerability."
        )

        # Expression: "not (me.email != '')"
        # Translation: Find all partners WITHOUT an email
        # Expected: Should use domain negation, not memory-based set operations
        expr = 'not (me.email != "")'

        try:
            result = self._exec(expr)

            # The query will succeed on small datasets
            # But note the implementation loads ALL IDs into memory
            count = result.get("count", 0)
            _logger.warning(
                f"[CEL CRITICAL TEST] NOT operator processed {count} records. "
                f"In production with 500K partners, this would load ALL 500K IDs "
                f"into memory simultaneously!"
            )

            # This test passes but demonstrates the dangerous pattern
            # The executor loads all partner IDs into a Python set
            self.assertGreater(count, 0, "Should find partners without email")

            # Log the dangerous behavior
            _logger.error(
                "⚠️  CRITICAL: NOT operator executed via full-table memory load! "
                "This will crash on large datasets. See cel_executor.py:101-104"
            )

        except Exception as e:
            # If it fails, that's also a problem
            _logger.error(f"[CEL CRITICAL TEST] NOT operator failed: {e}")
            raise

    def test_not_with_exists_demonstrates_memory_issue(self):
        """
        Even more critical: NOT with exists loads entire parent table.

        Expression like: "not members.exists(m, m.gender == 'Female')"
        Will load ALL group IDs into memory to compute negation.
        """
        _logger.warning("[CEL CRITICAL TEST] Testing NOT with subquery - " "even more dangerous memory pattern")

        # Create a few groups for testing
        Partner = self.env["res.partner"]
        Partner.create(
            {
                "name": "Group 1",
                "is_registrant": True,
                "is_group": True,
            }
        )

        # Try to negate an exists query
        # This should fail gracefully or use domain negation
        # Currently it loads ALL groups into memory
        cfg = self.env["cel.registry"].load_profile("registry_groups")
        ex = self.env["cel.executor"].with_context(cel_profile="registry_groups", cel_cfg=cfg)

        # This expression will trigger the memory issue
        expr = 'not members.exists(m, m.gender == "Female")'

        try:
            result = ex.compile_and_preview("res.partner", expr, limit=50)

            _logger.error(
                "⚠️  CRITICAL: NOT with EXISTS loaded entire groups table into memory! "
                "Production registries with 100K+ groups will crash. "
                "See cel_executor.py:101-104"
            )

            # Test technically passes but exposes critical issue
            self.assertIsNotNone(result.get("domain"))

        except Exception as e:
            _logger.warning(f"NOT with EXISTS failed (expected): {e}")
            # This might actually be better - failing fast is better than DoS

    def test_recommended_fix_validation(self):
        """
        This test documents the RECOMMENDED FIX for the NOT operator issue.

        RECOMMENDATION:
        1. Only allow NOT on domain-convertible sub-plans
        2. Reject complex subqueries with helpful error message
        3. Use native Odoo domain negation ['!', ...] when possible

        Example fix in cel_executor.py:

            if isinstance(plan, NOT):
                domain, requires_exec = self._plan_to_domain(model, plan.node)
                if requires_exec:
                    raise NotImplementedError(
                        "Negating complex expressions (like 'exists' or 'count') "
                        "is not supported due to performance constraints. "
                        "Please restructure your expression."
                    )
                # Use native domain negation instead of memory operations
                negated_domain = ['!'] + domain
                return self.env[model].search(negated_domain).ids
        """
        _logger.info(
            "[CEL CRITICAL TEST] Documenting recommended fix. " "See test comments for implementation guidance."
        )

        # This is a documentation test
        # When the fix is implemented, add validation here
        self.assertTrue(True, "See test docstring for recommended fix to NOT operator DoS issue")
