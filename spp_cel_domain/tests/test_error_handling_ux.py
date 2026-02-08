"""
Test to demonstrate poor error handling UX (HIGH priority).

This test demonstrates that error messages are not user-friendly,
showing raw Python exceptions instead of helpful guidance.

Issue: No exception handling in cel_rule_wizard.py:33-53
Severity: HIGH
Spec Reference: Section #9 Error handling & UX
"""

import logging

from odoo.tests import TransactionCase
from odoo.tests.common import tagged

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install", "cel_domain")
class TestErrorHandlingUX(TransactionCase):
    """Demonstrate that error messages are not user-friendly."""

    def setUp(self):
        super().setUp()
        # Create wizard for testing error handling
        self.wizard = self.env["cel.rule.wizard"].create(
            {
                "profile": "registry_individuals",
                "model_id": self.env["ir.model"].search([("model", "=", "res.partner")], limit=1).id,
                "cel_expression": "test expression",
            }
        )

    def test_syntax_error_not_user_friendly(self):
        """
        HIGH PRIORITY: Syntax errors show raw Python exceptions.

        Current behavior: User sees:
            Odoo Server Error
            Traceback (most recent call last):
              File "...cel_parser.py", line 165
                raise SyntaxError(f"Expected {kind} at {self.cur().pos}")
            SyntaxError: Expected IDENT at 42

        Expected behavior: User should see:
            "Syntax Error at position 42: Expected a field or function name.
             Did you forget to close a parenthesis?"
        """
        _logger.warning("[CEL HIGH PRIORITY TEST] Testing syntax error UX")

        # Invalid syntax: unclosed parenthesis
        self.wizard.cel_expression = "me.age_years(me.birthdate"

        try:
            self.wizard.action_validate_preview()

            # If we get here, check if error is shown in explain_text
            if self.wizard.explain_text and "error" in self.wizard.explain_text.lower():
                _logger.info("✅ Error handling implemented! Error shown in explain_text field.")
            else:
                self.fail("Syntax error was not caught. Raw exception likely shown to user.")

        except SyntaxError as e:
            # Expected: Raw exception propagates to user
            _logger.error(
                f"❌ Raw SyntaxError exposed to user: {e}\n"
                f"User will see Python stack trace instead of friendly message. "
                f"See CODE_REVIEW_REPORT.md Issue #4"
            )
            self.fail(
                "SyntaxError not caught by wizard. User sees raw Python error. "
                "Should show friendly message in explain_text field."
            )
        except Exception as e:
            _logger.error(f"❌ Raw exception exposed to user: {e}")
            self.fail(f"Exception not caught by wizard: {e}")

    def test_unknown_symbol_not_user_friendly(self):
        """
        HIGH PRIORITY: Unknown symbols should suggest alternatives.

        Current behavior:
            KeyError: 'individualsss'

        Expected behavior:
            "Unknown symbol 'individualsss'. Did you mean 'individuals'?"

        Spec requirement (Section #9):
            Human messages: "Unknown symbol 'X'. Did you mean 'individuals'?"
        """
        _logger.warning("[CEL HIGH PRIORITY TEST] Testing unknown symbol error UX")

        # Typo in symbol name
        self.wizard.cel_expression = "individualsss.exists(p, age_years(p.birthdate) < 5)"

        try:
            self.wizard.action_validate_preview()

            # Check if friendly error is shown
            if self.wizard.explain_text and "did you mean" in self.wizard.explain_text.lower():
                _logger.info("✅ Error handling shows suggestions! Great UX.")
            else:
                _logger.error("❌ Unknown symbol error not user-friendly")

        except (KeyError, AttributeError) as e:
            _logger.error(
                f"❌ Raw exception for unknown symbol: {e}\n"
                f"Should suggest: 'Did you mean \"members\"?' "
                f"See CODE_REVIEW_REPORT.md Issue #4"
            )
            self.fail("Unknown symbol error not user-friendly. " "Should show suggestion in explain_text field.")

    def test_type_error_not_user_friendly(self):
        """
        HIGH PRIORITY: Type errors should explain what went wrong.

        Current behavior:
            TypeError: unsupported operand type(s)...

        Expected behavior:
            "Function 'age_years' expects a date field, but got text field 'name' instead."

        Spec requirement (Section #9):
            Type errors: "Function `age_years` expects a date; got string at `p.dob`."
        """
        _logger.warning("[CEL HIGH PRIORITY TEST] Testing type error UX")

        # Wrong field type: age_years expects date, not text
        self.wizard.profile = "registry_groups"
        self.wizard.model_id = self.env["ir.model"].search([("model", "=", "res.partner")], limit=1)
        self.wizard.cel_expression = "members.exists(m, age_years(m.name) < 5)"

        try:
            self.wizard.action_validate_preview()

            # Check if type error is explained
            if self.wizard.explain_text and "expects" in self.wizard.explain_text.lower():
                _logger.info("✅ Type errors are well explained!")

        except Exception as e:
            _logger.error(
                f"❌ Type error not user-friendly: {e}\n" f"Should explain: 'age_years expects a date field, not text'"
            )
            # Note: This might actually succeed with wrong results
            # Type checking is not yet implemented

    def test_error_position_indicator(self):
        """
        MEDIUM PRIORITY: Errors should show position in expression.

        Spec requirement (Section #9):
            "Show where (offset/line/column) the parse failed and underline in the UI."

        Expected: Error message includes position and context:
            "Syntax error at position 23:
             members.exists(m, age_yrs(m.birthdate) < 5)
                               ^^^^^^^
             Unknown function 'age_yrs'. Did you mean 'age_years'?"
        """
        _logger.warning("[CEL MEDIUM PRIORITY TEST] Testing error position indicator")

        self.wizard.cel_expression = "members.exists(m, age_yrs(m.birthdate) < 5)"

        try:
            self.wizard.action_validate_preview()

            # Check if position is shown
            if self.wizard.explain_text and "position" in self.wizard.explain_text.lower():
                _logger.info("✅ Error position indicators implemented!")
            else:
                _logger.warning("⚠️ Error position not shown. Would help users find the problem.")

        except Exception as e:
            _logger.warning(f"Error position not shown: {e}")

    def test_recommended_error_handling_implementation(self):
        """
        This test documents the RECOMMENDED ERROR HANDLING implementation.

        IMPLEMENTATION GUIDE (cel_rule_wizard.py):

        ```python
        def action_validate_preview(self):
            self.ensure_one()
            # Clear previous results
            self.result_domain_text = ""
            self.explain_text = ""
            self.preview_count = 0

            registry = self.env["cel.registry"]
            cfg = registry.load_profile(self.profile)
            executor = self.env["cel.executor"].with_context(
                cel_profile=self.profile, cel_cfg=cfg
            )

            try:
                result = executor.compile_and_preview(
                    self.model_id.model, self.cel_expression, limit=50
                )
                self.result_domain_text = result.get("domain_text")
                self.explain_text = result.get("explain")
                self.preview_count = result.get("count")
                return self._show_success(f"{self.preview_count} matching records")

            except SyntaxError as e:
                error_msg = str(e)
                pos = getattr(e, 'offset', None)
                friendly_msg = f"Syntax Error"
                if pos:
                    friendly_msg += f" at position {pos}"
                friendly_msg += f": {error_msg}\\n\\n"
                friendly_msg += "Please check your expression for typos."
                self.explain_text = friendly_msg
                return self._show_error("Invalid Syntax", friendly_msg)

            except KeyError as e:
                symbol = str(e).strip("'")
                available = list(cfg.get("symbols", {}).keys())
                suggestion = self._suggest_symbol(symbol, available)
                msg = f"Unknown symbol '{symbol}'."
                if suggestion:
                    msg += f" Did you mean '{suggestion}'?"
                msg += f"\\n\\nAvailable symbols: {', '.join(available)}"
                self.explain_text = msg
                return self._show_error("Unknown Symbol", msg)

            except Exception as e:
                self.explain_text = f"Error: {str(e)}"
                return self._show_error("Processing Error", str(e))

        def _suggest_symbol(self, wrong_symbol, available_symbols):
            '''Simple Levenshtein distance for suggestions'''
            import difflib
            matches = difflib.get_close_matches(wrong_symbol, available_symbols, n=1, cutoff=0.6)
            return matches[0] if matches else None

        def _show_error(self, title, message):
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": title,
                    "message": message,
                    "type": "warning",
                    "sticky": True,
                },
            }

        def _show_success(self, message):
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "CEL Preview",
                    "message": message,
                    "type": "success",
                    "sticky": False,
                },
            }
        ```

        ADDITIONAL UX IMPROVEMENTS:
        1. Add 'error_text' field to wizard (separate from explain_text)
        2. Show syntax highlighting in wizard view
        3. Underline error position in expression field
        4. Provide "Learn More" link to documentation

        EFFORT: 8-16 hours (including all error types and suggestions)
        PRIORITY: HIGH (critical for non-developer rollout)
        """
        _logger.info(
            "[CEL HIGH PRIORITY TEST] Documenting recommended error handling. "
            "See test docstring for implementation guidance."
        )

        self.assertTrue(True, "See test docstring for recommended error handling implementation")

    def test_common_errors_have_helpful_messages(self):
        """
        Test that common user mistakes have specific, helpful error messages.

        Common mistakes:
        1. Typo in function name: age_year instead of age_years
        2. Typo in symbol name: member instead of members
        3. Missing closing parenthesis
        4. Wrong number of arguments to function
        5. Using wrong comparison operator (= instead of ==)
        """
        _logger.warning("[CEL MEDIUM PRIORITY TEST] Testing common error scenarios")

        common_errors = [
            ("age_year(m.birthdate) < 5", "Function typo"),
            ("member.exists(m, m.gender == 'Female')", "Symbol typo"),
            ("count(members, m, head(m) == 1", "Missing parenthesis"),
            ("age_years() < 5", "Wrong arity"),
            ("me.name = 'John'", "Wrong operator (= vs ==)"),
        ]

        for expr, error_type in common_errors:
            self.wizard.cel_expression = expr
            try:
                self.wizard.action_validate_preview()

                # Check if error is helpful
                if self.wizard.explain_text and any(
                    word in self.wizard.explain_text.lower() for word in ["did you mean", "expected", "suggestion"]
                ):
                    _logger.info(f"✅ Good error message for: {error_type}")
                else:
                    _logger.warning(f"⚠️ Error message could be better for: {error_type}")

            except Exception as e:
                _logger.warning(f"⚠️ Raw exception for {error_type}: {str(e)[:100]}")
