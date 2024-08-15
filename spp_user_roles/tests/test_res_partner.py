from unittest.mock import MagicMock, patch

from odoo.tests.common import TransactionCase


class ResPartnerTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.center_area_1 = cls.env["spp.area"].create({"draft_name": "Center Area 1"})
        cls.center_area_2 = cls.env["spp.area"].create({"draft_name": "Center Area 1"})
        cls.partner_1 = cls.env["res.partner"].create({"name": "Partner 1", "area_id": cls.center_area_1.id})
        cls.partner_2 = cls.env["res.partner"].create({"name": "Partner 2", "area_id": cls.center_area_2.id})

    def test_search_read(self):
        result = self.env["res.partner"].search_read(domain=[], fields=["id", "name", "area_id"])
        self.assertEqual(len(result), self.env["res.partner"].search_count([]))

        center_area_ids_mock = MagicMock()
        center_area_ids_mock.ids = self.center_area_1.ids

        with patch(
            "odoo.addons.spp_user_roles.models.user.ResUsersCustomSPP.center_area_ids", new=center_area_ids_mock
        ):
            result = self.env["res.partner"].search_read(domain=[], fields=["id", "name", "area_id"])

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result,
            [{"id": self.partner_1.id, "name": "Partner 1", "area_id": (self.center_area_1.id, "Center Area 1")}],
        )
