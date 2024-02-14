from odoo.tests import TransactionCase


class Common(TransactionCase):
    def setUp(self):
        super().setUp()
        self._model = self.env["spp.record.consent.wizard"]
        self._test_individual_1 = self._create_registrant({"name": "Tywin Lannister"})
        self._test_individual_2 = self._create_registrant({"name": "Jaime Lannister"})
        self._test_individual_3 = self._create_registrant({"name": "Cersei Lannister"})
        self._test_individual_4 = self._create_registrant({"name": "Tyrion Lannister"})
        self._test_group = self._create_registrant(
            {
                "name": "House Lannister",
                "is_group": True,
                "group_membership_ids": [
                    (
                        0,
                        0,
                        {
                            "individual": self._test_individual_1.id,
                            "kind": [
                                (
                                    4,
                                    self.env.ref("g2p_registry_membership.group_membership_kind_head").id,
                                )
                            ],
                        },
                    ),
                    (0, 0, {"individual": self._test_individual_2.id}),
                    (0, 0, {"individual": self._test_individual_3.id}),
                    (0, 0, {"individual": self._test_individual_4.id}),
                ],
            }
        )

    def _create_registrant(self, vals):
        self.assertTrue(isinstance(vals, dict), "Return vals should be a dict!")
        vals.update({"is_registrant": True})
        return self.env["res.partner"].create(vals)
