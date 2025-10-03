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

    def start_export(self):
        self.ensure_one()
        self.state = "in_progress"
        self.locked = True
        self.locked_reason = "Export in progress..."
    
    def refresh_page(self):
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }


class SPPDataExporterTemplates(models.Model):
    _name = "spp.data.exporter.templates"
    _description = "SPP Data Exporter Templates"

    name = fields.Char(string="Name", required=True)
    model_ids = fields.Many2many(
        "ir.model",
        string="Models",
        help="Select the models to include in the export template.",
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
