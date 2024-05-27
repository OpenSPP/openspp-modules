from odoo.tests import TransactionCase


class Common(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._model = cls.env["spp.record.consent.wizard"]
        cls._test_individual_1 = cls._create_registrant({"name": "Tywin Lannister"})
        cls._test_individual_2 = cls._create_registrant({"name": "Jaime Lannister"})
        cls._test_individual_3 = cls._create_registrant({"name": "Cersei Lannister"})
        cls._test_individual_4 = cls._create_registrant({"name": "Tyrion Lannister"})
        cls._test_group = cls._create_registrant(
            {
                "name": "House Lannister",
                "is_group": True,
                "group_membership_ids": [
                    (
                        0,
                        0,
                        {
                            "individual": cls._test_individual_1.id,
                            "kind": [
                                (
                                    4,
                                    cls.env.ref("g2p_registry_membership.group_membership_kind_head").id,
                                )
                            ],
                        },
                    ),
                    (0, 0, {"individual": cls._test_individual_2.id}),
                    (0, 0, {"individual": cls._test_individual_3.id}),
                    (0, 0, {"individual": cls._test_individual_4.id}),
                ],
            }
        )

    @classmethod
    def _create_registrant(self, vals):
        self.assertTrue(isinstance(vals, dict), "Return vals should be a dict!")
        vals.update({"is_registrant": True})
        return self.env["res.partner"].create(vals)
