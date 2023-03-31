from unittest.mock import patch

from odoo.tests import TransactionCase

from ..models.change_request import ChangeRequestBase


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

    @patch.object(
        ChangeRequestBase,
        "_selection_request_type_ref_id",
        return_value=[("test.request.type", "Test Request Type")],
    )
    def _create_change_request(self, name="Test Change Request"):
        return self.env["spp.change.request"].create(
            {"name": name, "request_type": "test.request.type"}
        )
