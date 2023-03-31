from odoo.tests import TransactionCase


class Common(TransactionCase):
    def setUp(self):
        self._test_individual_1 = self._create_registrant({"name": "Liu Bei"})
        self._test_individual_2 = self._create_registrant({"name": "Guan Yu"})
        self._test_individual_3 = self._create_registrant({"name": "Zhang Fei"})
        self._test_group = self._create_registrant(
            {
                "name": "Shu clan",
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
                                    self.env.ref(
                                        "g2p_registry_membership.group_membership_kind_head"
                                    ).id,
                                )
                            ],
                        },
                    ),
                    (0, 0, {"individual": self._test_individual_2.id}),
                    (0, 0, {"individual": self._test_individual_3.id}),
                ],
            }
        )
        return super().setUp()

    def _create_registrant(self, vals):
        assert type(vals) == dict
        vals.update({"is_registrant": True})
        return self.env["res.partner"].create(vals)

    def _create_test_queue(
        self, registrant_id, id_type=None, idpass_id=None, status="approved"
    ):
        if not id_type:
            id_type = self.env.ref("spp_idpass.id_type_idpass").id
        else:
            assert isinstance(id_type, int)
        if not idpass_id:
            idpass_id = self.env.ref("spp_idpass.id_template_idpass").id
        else:
            assert isinstance(idpass_id, int)
        assert status in ("new", "approved")
        return self.env["spp.print.queue.id"].create(
            {
                "registrant_id": registrant_id,
                "id_type": id_type,
                "requested_by": self.env.user.id,
                "status": status,
                "idpass_id": idpass_id,
            }
        )
