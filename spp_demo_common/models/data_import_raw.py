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
    json_data = fields.Text(string="JSON Data", readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("imported", "Imported"), ("error", "Error")],
        string="State",
        default="draft",
        required=True,
    )
    error_message = fields.Text(string="Error Message", readonly=True)
