# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import base64
import logging
from io import BytesIO

import pandas as pd

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class OpenSPPAreaImport(models.Model):
    _name = "spp.area.import"
    _description = "Areas Import Table"

    NEW = "New"
    UPLOADED = "Uploaded"
    IMPORTED = "Imported"
    VALIDATED = "Validated"
    DONE = "Done"
    CANCELLED = "Cancelled"

    STATE_SELECTION = [
        (NEW, NEW),
        (UPLOADED, UPLOADED),
        (IMPORTED, IMPORTED),
        (VALIDATED, VALIDATED),
        (DONE, DONE),
        (CANCELLED, CANCELLED),
    ]

    name = fields.Char("File Name", required=True)
    excel_file = fields.Binary("Area Excel File")
    date_uploaded = fields.Datetime()

    upload_id = fields.Many2one("res.users", "Uploaded by")
    date_imported = fields.Datetime()
    import_id = fields.Many2one("res.users", "Imported by")
    date_validated = fields.Datetime()
    validate_id = fields.Many2one("res.users", "Validated by")
    raw_data_ids = fields.One2many("spp.area.import.raw", "area_import_id", "Raw Data")
    tot_rows_imported = fields.Integer(
        "Total Rows Imported",
        compute="_compute_get_total_rows",
        store=True,
        readonly=True,
    )
    tot_rows_error = fields.Integer(
        "Total Rows with Error",
        compute="_compute_get_total_rows",
        store=True,
        readonly=True,
    )
    state = fields.Selection(
        STATE_SELECTION,
        "Status",
        default=NEW,
    )

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
                    "state": self.UPLOADED,
                }
            )
        else:
            self.update(
                {"date_uploaded": None, "upload_id": None, "state": self.UPLOADED}
            )

    @api.depends("raw_data_ids", "raw_data_ids.state")
    def _compute_get_total_rows(self):
        """
        This computes the total rows of the Excel file
        """
        for rec in self:
            tot_rows_imported = 0
            tot_rows_error = 0
            for ln in rec.raw_data_ids:
                tot_rows_imported += 1
                if ln.state == "Error":
                    tot_rows_error += 1
            rec.update(
                {
                    "tot_rows_imported": tot_rows_imported,
                    "tot_rows_error": tot_rows_error,
                }
            )

    def cancel_import(self):
        for rec in self:
            rec.update({"state": self.CANCELLED})

    def reset_to_uploaded(self):
        for rec in self:
            rec.update({"state": self.UPLOADED})

    def import_data(self):  # noqa: C901
        """
        This set up the datas from the Excel file then import it as raw data
        """
        _logger.info("Area Import: Started: %s" % fields.Datetime.now())
        for rec in self:

            # Delete all existing import data for this record
            # This can only be happen if the Area Upload record is reset back to Uploaded state
            if rec.raw_data_ids:
                rec.raw_data_ids.unlink()

            _logger.info("Area Import: Loading Excel File: %s" % fields.Datetime.now())
            # Wrap binary to BytesIO
            try:
                inputx = BytesIO()
                inputx.write(base64.decodebytes(rec.excel_file))
            except TypeError as e:
                raise ValidationError(_("ERROR: {}").format(e)) from e

            # Open file using pandas and get all sheet names of the excel
            # then sort sheet name from parent to child
            xl = pd.ExcelFile(inputx)
            sheet_names = xl.sheet_names
            sheet_names.sort()

            row_data_vals = []
            # Iterate sheet name and their index as area level
            for area_level, sheet_name in enumerate(sheet_names):

                # get sheet object by sheet name
                sheet = xl.parse(sheet_name)

                columns = sheet.columns

                # Get Column name to be used as name field in the area
                name_header = columns[0]

                # Get column prefix and the language iso code used in the name header
                column_name_prefix, name_iso_code = name_header.split("_")

                # Get Column name to be used as code field in the area
                code_header = f"{column_name_prefix}_PCODE"

                # Get Parent of the area if area level is not 0
                parent_name_header = None
                parent_code_header = None
                if area_level != 0:
                    parent_name_header = (
                        f"{column_name_prefix[:3]}{area_level - 1}_{name_iso_code}"
                    )
                    parent_code_header = (
                        f"{column_name_prefix[:3]}{area_level - 1}_PCODE"
                    )

                # Header for SQKM
                area_sqkm_header = "AREA_SQKM"

                # Get the required values for area in each row
                for _index, row in sheet.iterrows():
                    vals = {
                        "admin_name": row[name_header],
                        "admin_code": row[code_header],
                        "parent_name": "",
                        "parent_code": "",
                        "level": area_level,
                        "area_sqkm": row[area_sqkm_header],
                    }
                    if parent_name_header and parent_code_header:
                        vals.update(
                            {
                                "parent_name": row[parent_name_header],
                                "parent_code": row[parent_code_header],
                            }
                        )
                    row_data_vals.append([0, 0, vals])

            rec.update(
                {
                    "date_imported": fields.Datetime.now(),
                    "import_id": self.env.user,
                    "date_validated": fields.Datetime.now(),
                    "validate_id": self.env.user,
                    "state": self.IMPORTED,
                    "raw_data_ids": row_data_vals,
                }
            )

            _logger.info(
                "Area Masterlist Import: Completed: %s" % fields.Datetime.now()
            )

    def validate_raw_data(self):
        """
        This set up the data then save it to spp_area including the Area Type
        and its translations
        """
        for rec in self:
            has_error = rec.raw_data_ids.validate_raw_data()
            if not has_error:
                rec.update(
                    {
                        "state": self.VALIDATED,
                    }
                )

    def save_to_area(self):
        for rec in self:
            rec.raw_data_ids.save_to_area()
            rec.state = self.DONE


# Assets Import Raw Data
class OpenSPPAreaImportActivities(models.Model):
    _name = "spp.area.import.raw"
    _description = "Area Import Raw Data"
    _order = "level"

    NEW = "New"
    VALIDATED = "Validated"
    ERROR = "Error"
    UPDATED = "Updated"
    POSTED = "Posted"

    STATE_CHOICES = [
        (NEW, NEW),
        (VALIDATED, VALIDATED),
        (ERROR, ERROR),
        (UPDATED, UPDATED),
        (POSTED, POSTED),
    ]

    area_import_id = fields.Many2one("spp.area.import", "Area Import", required=True)
    admin_name = fields.Char()
    admin_code = fields.Char()

    parent_name = fields.Char()
    parent_code = fields.Char()

    level = fields.Integer()

    area_sqkm = fields.Char("Area (sq/km)")

    remarks = fields.Text("Remarks/Errors")
    state = fields.Selection(
        STATE_CHOICES,
        "Status",
        default="New",
    )

    def validate_raw_data(self):
        has_error = False
        for rec in self:
            errors = []
            if not rec.admin_name or not rec.admin_code:
                errors.append(_("Name and Code of area is required."))

            if rec.area_sqkm:
                try:
                    float(rec.area_sqkm)
                except ValueError:
                    errors.append(_("AREA_SQKM should be numerical."))

            if rec.level == 0 and (rec.parent_name or rec.parent_code):
                errors.append(
                    _("Level 0 area should not have a parent name and parent code.")
                )

            if rec.level != 0 and (not rec.parent_name or not rec.parent_code):
                errors.append(
                    _(
                        "Level 1 and above area should have a parent name and parent code."
                    )
                )

            if errors:
                state = self.ERROR
                remarks = "\n".join(errors)
                has_error = True
            else:
                state = self.VALIDATED
                remarks = "No Error"

            rec.write(
                {
                    "remarks": remarks,
                    "state": state,
                }
            )

        return has_error

    def save_to_area(self):
        for rec in self:
            parent_id = None
            if rec.parent_name and rec.parent_code:
                parent_id = (
                    self.env["spp.area"]
                    .search(
                        [
                            ("draft_name", "=", rec.parent_name),
                            ("code", "=", rec.parent_code),
                        ],
                        limit=1,
                    )
                    .id
                )

            area_sqkm = rec.area_sqkm

            try:
                area_sqkm = float(area_sqkm)
            except ValueError:
                area_sqkm = 0.0

            area_vals = {
                "parent_id": parent_id,
                "draft_name": rec.admin_name,
                "code": rec.admin_code,
                "area_sqkm": area_sqkm,
            }
            if area_id := self.env["spp.area"].search(
                [("draft_name", "=", rec.admin_name), ("code", "=", rec.admin_code)]
            ):
                state = self.UPDATED
                area_id.update(area_vals)
            else:
                state = self.POSTED
                self.env["spp.area"].create(area_vals)

            rec.update(
                {
                    "state": state,
                    "remarks": "Successfully save to Area",
                }
            )
