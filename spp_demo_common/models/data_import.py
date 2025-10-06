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
    summary_ids = fields.One2many("spp.data.importer.summary", "importer_id", string="Summary", readonly=True)

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("imported", "Imported"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
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
        self.raw_ids = False
        try:
            file_data = base64.b64decode(self.import_file)
            json_data = json.loads(file_data)
            raw_vals = []
            summary_data = []
            for data in json_data[1:]:
                model_name = data.get("model")
                summary_data.append(
                        {
                            "name": data.get("model", ""),
                            "importer_id": self.id,
                            "model_name": data.get("model", ""),
                            "record_count": data.get("record_count", 0),
                        }
                    )
                
                for record in data.get("data", []):
                    model_data = record
                    name = record.get("name", f"ID: {record.get('id', '')}")

                    raw_vals.append(
                        {
                            "name": name,
                            "model_name": model_name,
                            "importer_id": self.id,
                            "json_data": model_data,
                        }
                    )
            self.summary_ids = [(0, 0, vals) for vals in summary_data]
            self.raw_ids = [(0, 0, vals) for vals in raw_vals]
            self.state = "imported"
            self.locked = False
            self.locked_reason = "Import completed successfully."

        except Exception as e:
            raise ValidationError(f"Failed to parse import file: {e}") from e

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
        self.summary_ids = False
        if self.import_file:
            try:
                file_data = base64.b64decode(self.import_file)
                json_data = json.loads(file_data)
                modules = json_data[0].get("modules", [])
                if isinstance(modules, list):
                    self.module_list = ", ".join(modules)
                else:
                    self.module_list = modules or ""
                models = []
                for data in json_data[1:]:
                    models.append(data.get("model", ""))
                self.model_list = ", ".join(models)
            except Exception as e:
                raise ValidationError(f"Failed to parse import file: {e}") from e

    def refresh_page(self):
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }
