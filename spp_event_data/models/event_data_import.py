# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import base64
import logging
from io import BytesIO

from xlrd import open_workbook

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class OpenSPPEventDataImport(models.Model):
    _name = "spp.event.data.import"
    _description = "Areas Import Table"

    name = fields.Char("File Name", required=True)
    excel_file = fields.Binary("Event Data Excel File")
    date_uploaded = fields.Datetime()
    event_data_model = fields.Selection(
        selection="_selection_event_data_model_id", required=True
    )
    upload_id = fields.Many2one("res.users", "Uploaded by")
    date_imported = fields.Datetime()
    import_id = fields.Many2one("res.users", "Imported by")
    date_validated = fields.Datetime()
    validate_id = fields.Many2one("res.users", "Validated by")
    state = fields.Selection(
        [
            ("New", "New"),
            ("Uploaded", "Uploaded"),
            ("Imported", "Imported"),
            ("Done", "Done"),
            ("Cancelled", "Cancelled"),
        ],
        "Status",
        readonly=True,
        default="New",
    )

    @api.model
    def _selection_event_data_model_id(self):
        return []

    @api.onchange("excel_file")
    def excel_file_change(self):
        """
        This updates the date_uploaded, upload_id and state when
        the excel_file has been uploaded
        """
        if self.name:
            self.update(
                {
                    "date_uploaded": fields.Datetime.now(),
                    "upload_id": self.env.user,
                    "state": "Uploaded",
                }
            )
        else:
            self.update({"date_uploaded": None, "upload_id": None, "state": "New"})

    def cancel_import(self):
        for rec in self:
            rec.update({"state": "Cancelled"})

    def import_data(self):  # noqa: C901
        """
        This set up the datas from the Excel file then import it as raw data
        """
        _logger.info("Event Data Import: Started: %s" % fields.Datetime.now())
        for rec in self:
            _logger.info(
                "Event Data Import: Loading Excel File: %s" % fields.Datetime.now()
            )
            try:
                inputx = BytesIO()
                inputx.write(base64.decodebytes(rec.excel_file))
                book = open_workbook(file_contents=inputx.getvalue())
            except TypeError as e:
                raise ValidationError(_("ERROR: {}").format(e)) from e
            sheet = book.sheets()[0]
            _logger.info(
                "Event Data Import: Parsing Excel File: %s" % fields.Datetime.now()
            )
            function_name = rec.event_data_model
            function_name = function_name.replace(".", "_") + "_import"
            func = getattr(self, function_name)
            func(sheet)

    def save_to_event_data(self):
        """
        This set up the data then save it to event data and event data model
        """
        for rec in self:
            function_name = rec.event_data_model
            function_name = function_name.replace(".", "_") + "_save"
            func = getattr(self, function_name)
            func()
