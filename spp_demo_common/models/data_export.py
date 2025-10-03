import base64
import json
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SPPDataExporter(models.Model):
    _name = "spp.data.exporter"
    _description = "SPP Data Exporter"

    name = fields.Char(string="Name", required=True)
    template_id = fields.Many2one(
        "spp.data.exporter.templates", string="Template", help="Select the export template to use."
    )
    state = fields.Selection(
        [("draft", "Draft"), ("in_progress", "In Progress"), ("completed", "Completed"), ("cancelled", "Cancelled")],
        string="State",
        default="draft",
        required=True,
    )
    locked = fields.Boolean(string="Locked", default=False)
    locked_reason = fields.Text(string="Locked Reason")

    export_file = fields.Binary(string="Exported File", readonly=True)
    export_filename = fields.Char(string="Export Filename", readonly=True)

    template_module_ids = fields.Many2many(
        "ir.module.module",
        string="Modules",
        related="template_id.module_ids",
        readonly=True,
    )
    template_model_ids = fields.Many2many(
        "ir.model",
        string="Models",
        related="template_id.model_ids",
        readonly=True,
    )
    module_ids = fields.Many2many(
        "ir.module.module",
        string="Modules",
        help="Select the modules to include in the export.",
        compute="_compute_module_ids",
    )
    model_ids = fields.Many2many(
        "ir.model",
        string="Models",
        help="Select the models to include in the export.",
        compute="_compute_model_ids",
    )
    include_installed_modules = fields.Boolean(
        string="Include Installed Modules",
        default=False,
        help="Include all installed modules in the export.",
    )
    include_all_data = fields.Boolean(
        string="Include All Data",
        default=False,
        help="Include all data across the entire database in the export.",
    )
    raw_ids = fields.One2many(
        "spp.data.exporter.raw",
        "export_id",
        string="Raw Data",
        readonly=True,
    )

    def start_export(self):
        self.ensure_one()
        self.state = "in_progress"
        self.locked = True
        self.locked_reason = "Export in progress..."
        self.read_models_records()
        if self.raw_ids:
            export_data = []
            for raw in self.raw_ids:
                try:
                    json_data = json.loads(raw.json_data) if raw.json_data else []
                except Exception as e:
                    _logger.error(f"Error decoding JSON data for model {raw.model_name}: {e}")
                    json_data = []
                export_data.append(
                    {
                        "model": raw.model_name,
                        "record_count": raw.record_count,
                        "data": json_data,
                    }
                )
            export_filename = f"{self.name.replace(' ', '_').lower()}.json"
            json_bytes = json.dumps(export_data, indent=4).encode("utf-8")
            self.export_file = base64.b64encode(json_bytes)  # <-- base64 encode here
            self.export_filename = export_filename
            self.state = "completed"
            self.locked = False
            self.locked_reason = "Export completed successfully."

    def read_models_records(self):
        for rec in self:
            raw_data_records = []
            for model in rec.model_ids:
                model_obj = self.env[model.model]
                records = model_obj.search([])
                record_count = len(records)
                json_data = records.read() if record_count > 0 else []
                raw_data_records.append(
                    {
                        "name": model.model,
                        "model_name": model.name,
                        "record_count": record_count,
                        "json_data": json_data,
                        "export_id": rec.id,
                    }
                )
            self.env["spp.data.exporter.raw"].create(raw_data_records)

    def refresh_page(self):
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }

    @api.onchange("include_all_data")
    def _onchange_include_all_data(self):
        if self.include_all_data:
            self.include_installed_modules = True

    @api.depends("template_id", "include_installed_modules")
    def _compute_module_ids(self):
        for rec in self:
            rec.module_ids = False
            if rec.include_installed_modules:
                installed_modules = self.env["ir.module.module"].search([("state", "=", "installed")]).ids
                rec.module_ids = [(6, 0, installed_modules)]
            elif rec.template_id and not rec.include_installed_modules:
                rec.module_ids = [(6, 0, rec.template_id.module_ids.ids)]

    @api.depends("template_id", "include_all_data")
    def _compute_model_ids(self):
        for rec in self:
            rec.model_ids = False
            if rec.include_all_data:
                all_models = self.env["ir.model"].search([]).ids
                rec.model_ids = [(6, 0, all_models)]
            elif rec.template_id and not rec.include_all_data:
                rec.model_ids = [(6, 0, rec.template_id.model_ids.ids)]


class SPPDataExporterTemplates(models.Model):
    _name = "spp.data.exporter.templates"
    _description = "SPP Data Exporter Templates"

    name = fields.Char(string="Name", required=True)
    model_ids = fields.Many2many(
        "ir.model",
        string="Models",
        help="Select the models to include in the export template.",
        readonly=False,
        required=True,
    )
    module_ids = fields.Many2many(
        "ir.module.module",
        string="Modules",
        domain=[("state", "=", "installed")],
        help="Select the modules to include in the export template.",
        compute="_compute_module_ids",
        store=True,
    )
    active = fields.Boolean(string="Active", default=True)

    @api.depends("model_ids")
    def _compute_module_ids(self):
        for rec in self:
            module_ids = []
            for model in rec.model_ids:
                modules_list = [m.strip() for m in model.modules.split(",")] if model.modules else []
                for module_name in modules_list:
                    module = self.env["ir.module.module"].search([("name", "=", module_name)], limit=1)
                    if module and module.id not in module_ids:
                        module_ids.append(module.id)

            rec.module_ids = [(6, 0, module_ids)]
