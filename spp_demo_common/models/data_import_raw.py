import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class SPPDataImporterRaw(models.Model):
    _name = "spp.data.importer.raw"
    _description = "SPP Data Importer Raw"

    name = fields.Char(string="Name", required=True)
    model_name = fields.Char(string="Model Name", readonly=True)
    importer_id = fields.Many2one(
        "spp.data.importer",
        string="Importer",
        required=True,
    )
    record_id = fields.Integer(string="Record ID", readonly=True)
    db_id = fields.Integer(string="DB ID", readonly=True)
    json_data = fields.Text(string="JSON Data", readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("saved", "Saved"), ("error", "Error")],
        string="State",
        default="draft",
        required=True,
    )
    remarks = fields.Text(string="Remarks", readonly=True)


class SPPDataImporterSummary(models.Model):
    _name = "spp.data.importer.summary"
    _description = "SPP Data Importer Summary"

    name = fields.Char(string="Name", required=True)
    importer_id = fields.Many2one(
        "spp.data.importer",
        string="Importer",
        required=True,
    )
    model_name = fields.Char(string="Model Name", readonly=True)
    record_count = fields.Integer(string="Record Count", readonly=True)
    success_count = fields.Integer(string="Success Count", default=0, readonly=True)
    error_count = fields.Integer(string="Error Count", default=0, readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("completed", "Completed"), ("error", "Error")],
        string="State",
        default="draft",
        required=True,
    )
