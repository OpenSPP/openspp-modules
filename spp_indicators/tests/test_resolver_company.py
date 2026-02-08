from __future__ import annotations

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install", "spp_indicators")
class TestResolverCompany(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Resolver = self.env["openspp.indicator.resolver"].sudo()
        self.Company = self.env["res.company"].sudo()
        self.Partner = self.env["res.partner"].sudo()

        self.comp_a = self.env.company
        self.comp_b = self.Company.create({"name": "Indicators Co B"})

        # Same external ref in both companies
        self.p_a = self.Partner.create({"name": "A subject", "ref": "DUP-1", "company_id": self.comp_a.id})
        self.p_b = self.Partner.with_company(self.comp_b).create(
            {"name": "B subject", "ref": "DUP-1", "company_id": self.comp_b.id}
        )

    def test_resolve_external_ids_company_scoped(self):
        # Resolve in company A: should map to A record
        mapped_a, errors_a = (
            self.Resolver.with_company(self.comp_a)
            .sudo()
            .resolve_external_ids("res.partner", [{"index": 0, "external_id": "DUP-1"}], ["ref"], required=True)
        )
        self.assertEqual(mapped_a[0], self.p_a.id)
        self.assertFalse(errors_a)

        # Resolve in company B: should map to B record
        mapped_b, errors_b = (
            self.Resolver.with_company(self.comp_b)
            .sudo()
            .resolve_external_ids("res.partner", [{"index": 0, "external_id": "DUP-1"}], ["ref"], required=True)
        )
        self.assertEqual(mapped_b[0], self.p_b.id)
        self.assertFalse(errors_b)
