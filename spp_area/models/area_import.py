# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import base64
import logging
from io import BytesIO

from xlrd import open_workbook

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.queue_job.delay import group

_logger = logging.getLogger(__name__)


class OpenSPPAreaImport(models.Model):
    _name = "spp.area.import"
    _description = "Areas Import Table"

    MIN_ROW_JOB_QUEUE = 400

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

    locked = fields.Boolean(default=False)
    locked_reason = fields.Char(readonly=True)

    @api.onchange("excel_file")
    def excel_file_change(self):
        """
        The above function is an onchange function in Python that updates the date_uploaded, upload_id,
        and state fields based on the value of the excel_file field.
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
        The function `_compute_get_total_rows` calculates the total number of imported rows and the
        total number of rows with an error for a given record.
        """
        for rec in self:
            tot_rows_imported = len(rec.raw_data_ids)
            tot_rows_error = self.env["spp.area.import.raw"].search(
                [("id", "in", rec.raw_data_ids.ids), ("state", "=", "Error")]
            )
            rec.update(
                {
                    "tot_rows_imported": tot_rows_imported,
                    "tot_rows_error": len(tot_rows_error),
                }
            )

    def cancel_import(self):
        """
        The function cancels the import by updating the state of the record to "Cancelled".
        """
        for rec in self:
            rec.update({"state": self.CANCELLED})

    def reset_to_uploaded(self):
        """
        The function resets the state of a record to "Uploaded".
        """
        for rec in self:
            rec.update({"state": self.UPLOADED})

    def import_data(self):
        """
        The `import_data` function imports data from an Excel file, processes it, and updates the record
        with the imported data.
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

            # Open file using open_workbook, get all sheet names of the excel
            # then sort sheet name from parent to child
            book = open_workbook(file_contents=inputx.getvalue())

            sheet_names = book.sheet_names()
            sheet_names.sort()

            row_data_vals = []
            # Iterate sheet name and their index as area level
            for area_level, sheet_name in enumerate(sheet_names):
                # get sheet object by sheet name
                sheet = book.sheet_by_name(sheet_name)

                # get column list of sheet
                columns = sheet.row_values(0)

                # Get column prefix and the language iso code used in the name header
                name_iso_code = columns[0].split("_")[1]
                column_name_prefix = f"ADM{area_level}"

                # Get Column name to be used as name field in the area
                name_header = f"{column_name_prefix}_{name_iso_code}"

                # Get Column name to be used as code field in the area
                code_header = f"{column_name_prefix}_PCODE"

                # get name and code column indexes
                name_index = columns.index(name_header)
                code_index = columns.index(code_header)

                # Get index of the Parent header of the area if area level is not 0
                parent_name_index = None
                parent_code_index = None
                if area_level != 0:
                    parent_name_header = (
                        f"{column_name_prefix[:3]}{area_level - 1}_{name_iso_code}"
                    )
                    parent_code_header = (
                        f"{column_name_prefix[:3]}{area_level - 1}_PCODE"
                    )

                    parent_name_index = columns.index(parent_name_header)
                    parent_code_index = columns.index(parent_code_header)

                # Get area_sqkm column index
                area_sqkm_index = None
                if "AREA_SQKM" in columns:
                    area_sqkm_index = columns.index("AREA_SQKM")

                # Get the required values for area in each row
                for row in range(1, sheet.nrows):
                    vals = {
                        "admin_name": sheet.cell(row, name_index).value,
                        "admin_code": sheet.cell(row, code_index).value,
                        "parent_name": "",
                        "parent_code": "",
                        "level": area_level,
                    }
                    if area_sqkm_index:
                        vals.update(
                            {
                                "area_sqkm": sheet.cell(row, area_sqkm_index).value,
                            }
                        )
                    if parent_name_index is not None and parent_code_index is not None:
                        vals.update(
                            {
                                "parent_name": sheet.cell(row, parent_name_index).value,
                                "parent_code": sheet.cell(row, parent_code_index).value,
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
        The function iterates through a collection of records and checks if the count of raw data is
        less than a minimum threshold, and if so, it calls a validation function, otherwise it calls an
        asynchronous function.
        """
        for rec in self:
            raw_data_count = len(rec.raw_data_ids)
            if raw_data_count < self.MIN_ROW_JOB_QUEUE:
                rec._validate_raw_data()
            else:
                rec._async_function(
                    raw_data_count, _("Validating data."), "_validate_raw_data"
                )

    def _validate_raw_data(self):
        """
        The function validates raw data and updates the state if there are no errors.
        """
        self.ensure_one()

        has_error = self.raw_data_ids.validate_raw_data()
        if not has_error:
            self.update(
                {
                    "state": self.VALIDATED,
                }
            )

    def _async_function(self, raw_data_count, reason_message, function_name):
        """
        The above function is an asynchronous function that locks the current record, executes a delayed
        job, and marks the job as done when it completes.

        :param raw_data_count: The `raw_data_count` parameter represents the number of raw data items
        that will be processed in the async function
        :param reason_message: The `reason_message` parameter is a string that represents the reason for
        locking the object
        :param function_name: The `function_name` parameter is the name of the function that will be
        called asynchronously
        """
        self.ensure_one()

        self.write(
            {
                "locked": True,
                "locked_reason": reason_message,
            }
        )

        jobs = []

        func = getattr(self.delayable(channel="root.area_import"), function_name)

        jobs.append(func())

        main_job = group(*jobs)

        main_job.on_done(self.delayable(channel="root.area_import")._async_mark_done())
        main_job.delay()

    def _async_mark_done(self):
        """
        The function `_async_mark_done` unlocks a resource by setting the `locked` attribute to `False`
        and clearing the `locked_reason` attribute.
        """
        self.ensure_one()

        self.locked = False
        self.locked_reason = None

    def save_to_area(self):
        """
        The function saves data to an area, either synchronously or asynchronously depending on the
        number of raw data records.
        """
        for rec in self:
            raw_data_count = len(rec.raw_data_ids)

            if raw_data_count < self.MIN_ROW_JOB_QUEUE:
                rec._save_to_area()
            else:
                rec._async_function(
                    raw_data_count, _("Saving to Area."), "_save_to_area"
                )

    def _save_to_area(self):
        """
        The function saves raw data to an area and updates the state to "DONE".
        """
        self.ensure_one()

        self.raw_data_ids.save_to_area()
        self.state = self.DONE

    def refresh_page(self):
        """
        The function `refresh_page` returns a dictionary with the type and tag values to reload the
        page.
        :return: The code is returning a dictionary with two key-value pairs. The "type" key has the
        value "ir.actions.client" and the "tag" key has the value "reload".
        """
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }


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
        """
        The function `validate_raw_data` checks the validity of raw data by validating various fields
        and updating the state and remarks of each record accordingly.
        :return: a boolean value indicating whether there are any errors in the raw data. If there are
        errors, the value returned will be True. If there are no errors, the value returned will be
        False.
        """
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
        """
        The function saves data to the "spp.area" model in the database, updating existing records if
        they exist and creating new records if they don't.
        """
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
            if area_id := self.env["spp.area"].search([("code", "=", rec.admin_code)]):
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
