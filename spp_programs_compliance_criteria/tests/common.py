from odoo.tests import TransactionCase


class Common(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.areas = cls.env["spp.area"].create(
            [
                {"draft_name": "Area 1 [TEST]"},
                {"draft_name": "Area 2 [TEST]"},
                {"draft_name": "Area 3 [TEST]"},
            ]
        )
        cls._tag = cls.env["g2p.registrant.tags"].create({"name": "Tag 1 [TEST]"})

    @classmethod
    def program_create_wizard(self, vals):
        vals.update(
            {
                "name": "Program 1 [TEST]",
                "rrule_type": "monthly",
                "eligibility_domain": "[]",
                "cycle_duration": 1,
                "currency_id": self.env.company.currency_id.id,
                "admin_area_ids": [(6, 0, self.areas.ids)],
                "amount_per_cycle": 1.0,
            }
        )
        return self.env["g2p.program.create.wizard"].create(vals)
