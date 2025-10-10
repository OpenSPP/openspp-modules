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
    validated = fields.Boolean(string="Validated", default=False)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("validated", "Validated"),
            ("created", "Created"),
            ("saved", "Saved"),
            ("error", "Error"),
        ],
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
    success_count = fields.Integer(string="Success Count", compute="_compute_counts", readonly=True)
    validated_count = fields.Integer(string="Validated Count", compute="_compute_counts", readonly=True)
    error_count = fields.Integer(string="Error Count", compute="_compute_counts", readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("completed", "Completed"), ("partial", "Partial"), ("error", "Error")],
        string="State",
        compute="_compute_state",
    )

    def _compute_counts(self):
        for rec in self:
            importer_raw = rec.importer_id.raw_ids.filtered(
                lambda r, model_name=rec.model_name: r.model_name == model_name
            )
            rec.success_count = len(importer_raw.filtered(lambda r: r.state in ["saved", "created"]))
            rec.validated_count = len(importer_raw.filtered(lambda r: r.validated))
            rec.error_count = len(importer_raw.filtered(lambda r: r.state == "error"))

    def _compute_state(self):
        for rec in self:
            if rec.error_count > 0 and rec.success_count > 0:
                rec.state = "partial"
            elif rec.error_count > 0 and rec.success_count == 0:
                rec.state = "error"
            elif rec.success_count == rec.record_count and rec.record_count > 0:
                rec.state = "completed"
            else:
                rec.state = "draft"
