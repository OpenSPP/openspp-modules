from odoo.tests import TransactionCase


class Common(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._test_individual_1 = cls._create_registrant({"name": "Liu Bei"})
        cls._test_individual_2 = cls._create_registrant({"name": "Guan Yu"})
        cls._test_individual_3 = cls._create_registrant({"name": "Zhang Fei"})
        cls._test_group = cls._create_registrant(
            {
                "name": "Shu clan",
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
                ],
            }
        )

    @classmethod
    def _create_registrant(self, vals):
        self.assertTrue(isinstance(vals, dict), "Return vals should be a dict!")
        vals.update({"is_registrant": True})
        return self.env["res.partner"].create(vals)

    @classmethod
    def _create_test_queue(self, registrant_id, id_type=None, idpass_id=None, status="approved"):
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
