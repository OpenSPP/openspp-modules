from odoo.tests import TransactionCase

from ..services import cel_parser as P


class TestCelParser(TransactionCase):
    def test_simple_compare(self):
        ast = P.parse('age_years(me.birthdate) < 5 and me.district in ["A","B"]')
        self.assertTrue(ast)

    def test_string_with_escaped_quote(self):
        ast = P.parse('me.name == "John "The Rock" Doe"')
        self.assertTrue(ast)

    def test_unknown_character_raises(self):
        with self.assertRaises(SyntaxError):
            P.parse("amount > 100;")
