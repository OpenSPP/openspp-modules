from unittest.mock import MagicMock, patch

from odoo import fields
from odoo.tests.common import TransactionCase


class PMTTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.area_1 = cls.env["spp.area"].create(
            {
                "draft_name": "Area 1",
            }
        )
        cls.registrant_1 = cls.env["res.partner"].create(
            {
                "family_name": "Butay",
                "given_name": "Red",
                "name": "Red Butay",
                "is_group": False,
                "is_registrant": True,
                "area_id": cls.area_1.id,
            }
        )
        cls.group_1 = cls.env["res.partner"].create(
            {
                "name": "Group 1",
                "is_group": True,
                "is_registrant": True,
                "area_id": cls.area_1.id,
            }
        )
        cls.group_membership_1 = cls.env["g2p.group.membership"].create(
            {
                "group": cls.group_1.id,
                "individual": cls.registrant_1.id,
                "start_date": fields.Datetime.now(),
            }
        )

    def test_compute_area(self):
        self.registrant_1._compute_area()
        self.assertFalse(self.registrant_1.area_calc.id)

        self.group_1._compute_area()
        self.assertEqual(self.group_1.area_calc.id, self.area_1.id)

    def test_compute_score(self):
        self.group_1.compute_score("z_ind_grp_pmt_score")
        self.assertEqual(self.group_1.z_ind_grp_pmt_score, 0)

    @patch("odoo.addons.base.models.ir_model.IrModelFields.search")
    def test_compute_score_with_weight(self, mock_search):
        area_id = self.env["spp.fields.area"].create(
            {
                "name": self.area_1.id,
                "weight": 1.0,
            }
        )
        self.registrant_1.z_ind_grp_num_individuals = 1

        mock_fields = MagicMock()
        mock_fields.name = "z_ind_grp_num_individuals"
        mock_fields.with_weight = True
        mock_fields.target_type = "indv"
        mock_fields.area_ids = area_id
        mock_search.return_value = [mock_fields]

        self.group_1.compute_score("z_ind_grp_pmt_score")
        self.assertEqual(self.group_1.z_ind_grp_pmt_score, 1)
