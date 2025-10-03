import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class SPPDataExporterRaw(models.Model):
    _name = "spp.data.exporter.raw"
    _description = "SPP Data Exporter Raw"

    name = fields.Char(string="Name", required=True)
    model_id = fields.Many2one(
        "ir.model",
        string="Model",
        required=True,
    )
    export_id = fields.Many2one(
        "spp.data.exporter",
        string="Export",
        required=True,
    )
    record_count = fields.Integer(string="Record Count", readonly=True)
    json_data = fields.Text(string="JSON Data", readonly=True)
