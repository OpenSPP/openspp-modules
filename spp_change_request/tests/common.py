from unittest.mock import patch

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

    @patch(
        "odoo.addons.spp_change_request.models.change_request.ChangeRequestBase._selection_request_type_ref_id"
    )
    def _create_change_request(self, mock_request_type_selection):
        mock_request_type_selection.return_value = [
            ("test.request.type", "Test Request Type")
        ]
        mock_request_type_selection.__name__ = "_mocked__selection_request_type_ref_id"
        return self.env["spp.change.request"].create(
            {
                "name": "Test Request",
                "request_type": "test.request.type",
            }
        )
