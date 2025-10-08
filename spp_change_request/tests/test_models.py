from odoo import api, fields, models


class TestCRType(models.Model):
    _name = "test.cr.type2"
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

    validation_ids = fields.Many2many("spp.change.request.validation.sequence", string="Validations")

    def update_live_data(self):
        return

    @api.onchange("registrant_id")
    def _onchange_registrant_id(self):
        pass


class SPPDMSDirectory(models.Model):
    _inherit = "spp.dms.directory"

    change_request_test_cr_id = fields.Many2one(
        "test.cr.type2",
        string="Change Request (Test CR Type)",
    )


class SPPDMSFile(models.Model):
    _inherit = "spp.dms.file"

    change_request_test_cr_id = fields.Many2one(
        "test.cr.type2",
        string="Change Request (Test CR Type)",
    )
