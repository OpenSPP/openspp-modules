from odoo import fields, models


class TestCRType(models.Model):
    _name = "test.cr.type"
    _inherit = "spp.change.request.source.mixin"
    _description = "Test CR Type for Source Mixin"
    _test = True  # Mark this as a test model

    dms_directory_ids = fields.One2many(
        "spp.dms.directory",
        "change_request_test_cr_id",
        string="DMS Directories",
        auto_join=True,
    )
    dms_file_ids = fields.One2many(
        "spp.dms.file",
        "change_request_test_cr_id",
        string="DMS Files",
        auto_join=True,
    )

    def update_live_data(self):
        return super().update_live_data()


class SPPDMSDirectory(models.Model):
    _inherit = "spp.dms.directory"

    change_request_test_cr_id = fields.Many2one(
        "test.cr.type",
        string="Change Request (Test CR Type)",
    )


class SPPDMSFile(models.Model):
    _inherit = "spp.dms.file"

    change_request_test_cr_id = fields.Many2one(
        "test.cr.type",
        string="Change Request (Test CR Type)",
    )
