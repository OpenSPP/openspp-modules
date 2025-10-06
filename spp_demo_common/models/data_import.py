import base64
import json
import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SPPDataImporter(models.Model):
    _name = "spp.data.importer"
    _description = "SPP Data Importer"

    name = fields.Char(string="Name", required=True)
    import_file = fields.Binary(string="Import File", required=True)
    import_filename = fields.Char(string="Import Filename", required=True)

    module_ids = fields.Many2many(
        "ir.module.module",
        string="Modules",
        help="Select the modules to include in the export.",
        compute="_compute_module_ids",
    )
    module_list = fields.Text(string="Module List", readonly=True)

    model_ids = fields.Many2many(
        "ir.model",
        string="Models",
        help="Select the models to include in the export.",
        compute="_compute_model_ids",
    )
    model_list = fields.Text(string="Model List", readonly=True)

    raw_ids = fields.One2many("spp.data.importer.raw", "importer_id", string="Raw Data", readonly=True)

    state = fields.Selection(
        [("draft", "Draft"), ("in_progress", "In Progress"), ("completed", "Completed"), ("cancelled", "Cancelled")],
        string="State",
        default="draft",
        required=True,
    )
    locked = fields.Boolean(string="Locked", default=False)
    locked_reason = fields.Text(string="Locked Reason")

    def start_import(self):
        self.ensure_one()
        self.state = "in_progress"
        self.locked = True
        self.locked_reason = "Import in progress..."

    @api.depends("module_list")
    def _compute_module_ids(self):
        for rec in self:
            rec.module_ids = False
            if rec.module_list:
                module_names = [name.strip() for name in rec.module_list.split(",") if name.strip()]
                modules = self.env["ir.module.module"].search([("name", "in", module_names)])
                rec.module_ids = modules

    @api.depends("model_list")
    def _compute_model_ids(self):
        for rec in self:
            rec.model_ids = False
            if rec.model_list:
                model_names = [name.strip() for name in rec.model_list.split(",") if name.strip()]
                models = self.env["ir.model"].search([("model", "in", model_names)])
                rec.model_ids = models

    @api.onchange("import_file")
    def _onchange_import_file(self):
        self.module_list = ""
        self.model_list = ""
        if self.import_file:
            try:
                file_data = base64.b64decode(self.import_file)
                json_data = json.loads(file_data)
                self.module_list = json_data[0].get("modules", "")
            except Exception as e:
                raise ValidationError(f"Failed to parse import file: {e}") from e

    def refresh_page(self):
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }
