from odoo import fields, models


class TestDailyRecomputeModel(models.TransientModel):
    _name = "spp.test.daily.recompute.model"
    _description = "Test Daily Recompute Model"

    field_to_test_1 = fields.Char(
        string="Field to Test 1",
        compute="_compute_field_to_test_1",
        store=True,
        recompute_daily=True,
    )
    # test recompute daily with compute non-stored field
    field_to_test_2 = fields.Char(
        string="Field to Test 2",
        compute="_compute_field_to_test_2",
        store=False,
        recompute_daily=True,
    )
    # test recompute daily with non-computed field
    field_to_test_3 = fields.Char(
        string="Field to Test 3",
        recompute_daily=True,
    )

    def _compute_field_to_test_1(self):
        for rec in self:
            rec.field_to_test_1 = "1"

    def _compute_field_to_test_2(self):
        for rec in self:
            rec.field_to_test_2 = "2"
