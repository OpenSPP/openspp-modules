# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import base64
import datetime
import json
import logging
import math
import time
from io import BytesIO

import pandas as pd
from openpyxl import load_workbook

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.queue_job.delay import group

_logger = logging.getLogger(__name__)
_area_import_raw_model = "spp.area.import.raw"
_res_lang_model = "res.lang"
_area_import_channel = "root.area_import"


class OpenSPPAreaImport(models.Model):
    _name = "spp.area.import"
    _description = "Areas Import Table"
    _users_model = "res.users"

    JOB_QUEUE_BATCH_SIZE = 100

    NEW = "New"
    UPLOADED = "Uploaded"
    PARSED = "Parsed"
    IMPORTED = "Imported"
    VALIDATED = "Validated"
    DONE = "Done"
    CANCELLED = "Cancelled"

    STATE_SELECTION = [
        (NEW, NEW),
        (UPLOADED, UPLOADED),
        (PARSED, PARSED),
        (IMPORTED, IMPORTED),
        (VALIDATED, VALIDATED),
        (DONE, DONE),
        (CANCELLED, CANCELLED),
    ]

    name = fields.Char("File Name", required=True, translate=True)
    excel_file = fields.Binary("Area Excel File")
    date_uploaded = fields.Datetime()

    upload_id = fields.Many2one(_users_model, "Uploaded by")
    date_parsed = fields.Datetime()
    parse_id = fields.Many2one(_users_model, "Parsed by")
    json_file_ids = fields.One2many("spp.area.import.json", "area_import_id", "JSON Files")
    date_imported = fields.Datetime()
    import_id = fields.Many2one(_users_model, "Imported by")
    date_validated = fields.Datetime()
    validate_id = fields.Many2one(_users_model, "Validated by")
    raw_data_ids = fields.One2many(_area_import_raw_model, "area_import_id", "Raw Data")
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
    locked_reason = fields.Text(readonly=True)
    missing_languages = fields.Text(readonly=True)

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
            self.update({"date_uploaded": None, "upload_id": None, "state": self.UPLOADED})

    @api.depends("raw_data_ids", "raw_data_ids.state")
    def _compute_get_total_rows(self):
        """
        The function `_compute_get_total_rows` calculates the total number of imported rows and the
        total number of rows with an error for a given record.
        """
        for rec in self:
            tot_rows_imported = len(rec.raw_data_ids)
            tot_rows_error = self.env[_area_import_raw_model].search(
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
        Cancel the import and create a new import record to start fresh.
        Redirects to the newly created record.
        """
        for rec in self:
            rec.update({"state": self.CANCELLED})

        # Create a new area import record
        new_record = self.env["spp.area.import"].create(
            {
                "name": _("New Area Import"),
                "state": self.NEW,
            }
        )

        # Return action to open the new record in form view
        return {
            "type": "ir.actions.act_window",
            "res_model": "spp.area.import",
            "res_id": new_record.id,
            "view_mode": "form",
            "target": "current",
            "context": self.env.context,
        }

    def reset_to_uploaded(self):
        """
        The function resets the state of a record to "Uploaded".
        """
        for rec in self:
            rec.update({"state": self.UPLOADED})

    def get_cell_value(self, sheet, row, col):
        # openpyxl worksheet
        # if isinstance(sheet, (Worksheet, ReadOnlyWorksheet)):
        #     return sheet.cell(row=row+1, column=col+1).value
        # else:
        #     # xlrd sheet
        return sheet.cell(row, col).value

    def _get_book(self):
        self.ensure_one()
        try:
            inputx = BytesIO()
            inputx.write(base64.decodebytes(self.excel_file))
        except TypeError as e:
            raise ValidationError(_("ERROR: {}").format(e)) from e

        filename = self.name.lower()
        if filename.endswith(".xlsx"):
            # Try to open with openpyxl first for .xlsx files
            try:
                book = load_workbook(inputx, read_only=True)
                return book
            except Exception as e:
                _logger.warning("Failed to open with openpyxl: %s", e)
        else:
            raise ValidationError(_("ERROR: Unsupported file format. Please upload a .xlsx file."))

    def get_sheet_openpyxl(self, book, name):
        return book[name]

    def get_columns_openpyxl(self, sheet):
        return [cell.value for cell in next(sheet.iter_rows(min_row=1, max_row=1))]

    def parse_excel_to_json(self):
        """
        Trigger async job to parse Excel file to JSON format using pandas.
        Uses pandas for 2-3x faster parsing compared to openpyxl.
        Suitable for files up to 100k+ rows.
        """
        self.ensure_one()
        _logger.info("Area Import: Starting Excel parse to JSON with pandas: %s" % fields.Datetime.now())

        self.locked = True
        self.locked_reason = _("Parsing Excel file to JSON with pandas.")

        # Create single job to parse Excel with pandas
        job = self.delayable(channel=_area_import_channel)._scan_and_create_parse_jobs()
        # After parsing, import the data
        job.on_done(self.delayable(channel=_area_import_channel).after_parse())
        job.delay()
    
    def after_parse(self):
        """
        After parsing, import the data.
        """
        self.ensure_one()
        with_missing_languages = self._validate_languages_activated()
        if with_missing_languages:
            missing_languages = ", ".join(with_missing_languages)
            self.update({
                "locked": True,
                "locked_reason": None,
                "missing_languages": missing_languages,
            })
            return
        self.import_data()

    def activate_languages(self):
        """
        Activate the languages found in the import file.
        """
        self.ensure_one()
        missing_languages = list(set(self.missing_languages.split(", ")))
        for lang in missing_languages:
            lang = lang.strip().lower()
            _logger.info(f"Area Import: Activating language: {lang}")
            if lang:
                language = self.env[_res_lang_model].search([("iso_code", "=", lang)])
                if language:
                    language.write({"active": True})
        self.update({
            "missing_languages": None,
            "locked_reason": None,
            "locked": False,
        })
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }

    def _scan_and_create_parse_jobs(self):
        """
        Parse Excel file using pandas for 2-3x faster performance.
        Loads entire file into memory and creates JSON batches in a single pass.
        Memory-efficient for files up to 100k+ rows.
        """
        self.ensure_one()
        parse_start = time.time()
        _logger.info("Area Import: Parsing Excel file with pandas at %s", fields.Datetime.now())

        # Clear existing JSON files
        if self.json_file_ids:
            self.json_file_ids.unlink()

        # Load Excel file
        load_start = time.time()
        file_data = BytesIO(base64.decodebytes(self.excel_file))

        # Read all sheets at once (pandas is much faster than openpyxl)
        try:
            all_sheets = pd.read_excel(file_data, sheet_name=None, engine="openpyxl")
        except Exception as e:
            _logger.error(f"Error reading Excel file with pandas: {e}")
            raise ValidationError(_("Error reading Excel file: {}").format(str(e))) from e

        load_time = time.time() - load_start
        _logger.info(f"Area Import: Excel file loaded in {load_time:.2f} seconds")

        # Track batches and rows
        batch_number = 0
        total_rows = 0
        total_batches = 0
        sheet_names = sorted(all_sheets.keys())

        # Process each sheet
        for area_level, sheet_name in enumerate(sheet_names):
            sheet_start = time.time()
            df = all_sheets[sheet_name]

            _logger.info(f"Area Import: Processing sheet '{sheet_name}' at level {area_level}")
            _logger.info(f"Area Import: Sheet has {len(df)} rows and {len(df.columns)} columns")

            # Drop completely empty rows
            df = df.dropna(how="all")

            if df.empty:
                _logger.info(f"Area Import: Sheet '{sheet_name}' is empty, skipping")
                continue

            # Get column names (headers)
            headers = df.columns.tolist()

            # Process in batches
            sheet_rows = 0
            batch_start = time.time()

            for start_idx in range(0, len(df), self.JOB_QUEUE_BATCH_SIZE):
                end_idx = min(start_idx + self.JOB_QUEUE_BATCH_SIZE, len(df))
                batch_df = df.iloc[start_idx:end_idx]

                # Convert batch to list of dicts (JSON-ready format)
                rows = []
                for __, row in batch_df.iterrows():
                    row_data = {
                        "_sheet_name": sheet_name,
                        "_area_level": area_level,
                    }

                    # Add all columns
                    for col in headers:
                        value = row[col]

                        # Handle pandas-specific types
                        if pd.isna(value):
                            value = None
                        elif isinstance(value, pd.Timestamp):
                            value = value.isoformat()
                        elif isinstance(value, datetime.datetime | datetime.date):
                            value = value.isoformat()

                        row_data[col] = value

                    rows.append(row_data)

                # Create JSON file for this batch
                if rows:
                    self._create_json_file(batch_number, rows, batch_start)
                    batch_number += 1
                    total_batches += 1
                    sheet_rows += len(rows)
                    total_rows += len(rows)
                    batch_start = time.time()

                # Log progress every 1000 rows
                if total_rows % 1000 == 0:
                    elapsed = time.time() - parse_start
                    rate = total_rows / elapsed if elapsed > 0 else 0
                    _logger.info(f"Area Import: Parsed {total_rows} rows in {elapsed:.2f}s ({rate:.0f} rows/s)")

            sheet_time = time.time() - sheet_start
            _logger.info(f"Area Import: Completed sheet '{sheet_name}' - {sheet_rows} rows in {sheet_time:.2f} seconds")

        # Mark parsing as done
        total_time = time.time() - parse_start
        avg_time = total_time / total_rows if total_rows > 0 else 0
        rows_per_sec = total_rows / total_time if total_time > 0 else 0

        _logger.info(
            f"Area Import: Completed parsing {total_rows} rows into {total_batches} JSON files "
            f"in {total_time:.2f} seconds ({rows_per_sec:.0f} rows/s, avg {avg_time:.4f}s per row)"
        )

        # Update state directly (no need for separate job)
        self.update(
            {
                "date_parsed": fields.Datetime.now(),
                "parse_id": self.env.user,
                "state": self.PARSED,
            }
        )

        self.locked = False
        self.locked_reason = None

    def _create_json_file(self, batch_number, rows, batch_start):
        """
        Create a JSON file from a batch of rows and store it as binary.
        """
        json_start = time.time()
        json_string = json.dumps(rows)
        json_bytes = json_string.encode("utf-8")
        json_time = time.time() - json_start

        batch_time = time.time() - batch_start

        _logger.info(
            f"Area Import: Creating JSON file for batch {batch_number} with {len(rows)} rows "
            f"(batch time: {batch_time:.2f}s, JSON serialization: {json_time:.4f}s, "
            f"size: {len(json_bytes)} bytes)"
        )

        # Create JSON file record
        self.env["spp.area.import.json"].create(
            {
                "area_import_id": self.id,
                "batch_number": batch_number,
                "json_file_name": f"batch_{batch_number}.json",
                "json_file": base64.b64encode(json_bytes),
                "row_count": len(rows),
                "file_size": len(json_bytes),
            }
        )

    def import_data(self):
        """
        Import data from parsed JSON files into raw data records.
        Each JSON file is processed as a separate batch job.
        """
        self.ensure_one()
        _logger.info("Area Import: Started importing from JSON files: %s" % fields.Datetime.now())

        if self.raw_data_ids:
            self.raw_data_ids.unlink()

        if not self.json_file_ids:
            raise ValidationError(_("No JSON files found. Please parse the Excel file first."))

        # Validate languages before importing
        missing_languages = self._validate_languages_activated()
        if missing_languages:
            error_message = _(
                "The following languages are found in the import file " "but not activated in the system:\n\n"
            )
            error_message += "\n".join([f"  • {lang}" for lang in missing_languages])
            error_message += _("\n\nPlease activate these languages in the system before importing.\n")
            self.update({
                "locked": True,
                "locked_reason": None,
                "missing_languages": missing_languages,
            })
            raise ValidationError(error_message)

        self.locked = True
        self.locked_reason = _("Importing data from JSON files.")
        self.missing_languages = None
        jobs = []

        # Create a job for each JSON file batch
        for json_file in self.json_file_ids.sorted(lambda x: x.batch_number):
            jobs.append(self.delayable(channel=_area_import_channel)._import_data_from_json(json_file.id))

        main_job = group(*jobs)
        main_job.on_done(self.delayable(channel=_area_import_channel)._async_mark_done("_import_mark_done"))
        main_job.delay()

    def _validate_languages_activated(self):
        """
        Check if all languages found in JSON files are activated in Odoo.
        Raises ValidationError if any languages are not activated.
        """
        self.ensure_one()
        _logger.info("Area Import: Validating languages...")

        # Get the first JSON file to check languages
        first_json_file = self.json_file_ids.sorted(lambda x: x.batch_number)[0]

        # Decode and parse JSON
        json_bytes = base64.b64decode(first_json_file.json_file)
        json_string = json_bytes.decode("utf-8")
        rows = json.loads(json_string)

        if not rows:
            return

        # Get first row to check available languages
        first_row = rows[0]

        # Find all language codes in the JSON
        found_languages = set()
        for key in first_row.keys():
            # Check for ADM pattern with language code (e.g., ADM0_EN, ADM1_FR)
            if key.startswith("ADM") and "_" in key:
                parts = key.split("_")
                if len(parts) >= 2:
                    # Last part should be language code (e.g., EN, FR, ES)
                    lang_code = parts[-1]
                    # Only consider 2-letter codes (avoid PCODE, SQKM, etc.)
                    if len(lang_code) == 2 and lang_code.isalpha():
                        found_languages.add(lang_code.upper())

        _logger.info(f"Area Import: Found languages in JSON: {', '.join(found_languages)}")

        # Get active languages in Odoo
        active_languages = self.env[_res_lang_model].search([("active", "=", True)])
        active_iso_codes = {lang.iso_code.upper() for lang in active_languages}

        # Check for missing languages
        missing_languages = found_languages - active_iso_codes
        return sorted(missing_languages)

    def _import_data_from_json(self, json_file_id):
        """
        Import data from a single JSON file batch.
        Extracts area information based on the highest level in each row.
        Handles multi-language translations from Excel columns (ADM{level}_{LANG_CODE}).
        """
        self.ensure_one()
        import_start = time.time()

        json_file_record = self.env["spp.area.import.json"].browse(json_file_id)
        _logger.info(
            f"Area Import: Processing {json_file_record.json_file_name} " f"(batch {json_file_record.batch_number})"
        )

        # Decode and parse JSON
        json_bytes = base64.b64decode(json_file_record.json_file)
        json_string = json_bytes.decode("utf-8")
        rows = json.loads(json_string)

        _logger.info(f"Area Import: Loaded {len(rows)} rows from {json_file_record.json_file_name}")

        # Get active languages for mapping ISO codes
        active_languages = self.env[_res_lang_model].search([("active", "=", True)])
        lang_mapping = {lang.iso_code.upper(): lang.code for lang in active_languages}

        # Process each row
        for idx, row_data in enumerate(rows):
            row_start = time.time()

            area_level = row_data.get("_area_level", 0)

            # Extract current level fields (highest level in this row)
            admin_code_key = f"ADM{area_level}_PCODE"
            admin_code = row_data.get(admin_code_key)

            # Get default EN value directly
            default_name = row_data.get(f"ADM{area_level}_EN")

            # Find all translations for this level
            admin_level_prefix = f"ADM{area_level}_"
            translations = {"en_US": default_name}  # Start with EN as default

            for key, value in row_data.items():
                if key.startswith(admin_level_prefix) and key != admin_code_key:
                    lang_code = key.replace(admin_level_prefix, "")
                    if lang_code != "EN" and lang_code in lang_mapping:
                        # If empty or None, use default EN value
                        if not value or not value.strip():
                            translations[lang_mapping[lang_code]] = default_name
                        else:
                            translations[lang_mapping[lang_code]] = value

            # Extract parent level fields (one level lower)
            parent_name = None
            parent_code = None
            if area_level > 0:
                parent_level = area_level - 1
                parent_name_key = f"ADM{parent_level}_EN"  # Use EN for parent name
                parent_code_key = f"ADM{parent_level}_PCODE"
                parent_name = row_data.get(parent_name_key)
                parent_code = row_data.get(parent_code_key)

            # Create raw import record with default name
            raw_vals = {
                "area_import_id": self.id,
                "admin_name": default_name,
                "admin_code": admin_code,
                "parent_name": parent_name,
                "parent_code": parent_code,
                "level": area_level,
                "area_sqkm": row_data.get("AREA_SQKM"),
            }

            raw_record = self.env[_area_import_raw_model].create(raw_vals)

            # Update translations for all languages found
            for lang_code, translated_name in translations.items():
                if lang_code != "en_US":  # Skip default language (already set)
                    raw_record.with_context(lang=lang_code).write(
                        {
                            "admin_name": translated_name,
                        }
                    )

            row_time = time.time() - row_start
            if (idx + 1) % 10 == 0:  # Log every 10 rows
                _logger.info(
                    f"Area Import: Processed {idx + 1}/{len(rows)} rows from batch "
                    f"{json_file_record.batch_number} (last row: {row_time:.4f}s, "
                    f"translations: {len(translations)})"
                )

        batch_time = time.time() - import_start
        _logger.info(
            f"Area Import: Completed batch {json_file_record.batch_number} - " f"{len(rows)} rows in {batch_time:.2f}s"
        )

    def _import_mark_done(self):
        """
        Mark the import as done after all batch jobs have completed.
        Called by _async_mark_done() after all JSON files have been processed.
        """
        self.ensure_one()

        # Update state to imported
        self.update(
            {
                "date_imported": fields.Datetime.now(),
                "import_id": self.env.user,
                "state": self.IMPORTED,
            }
        )

        _logger.info(
            "Area Import: All batches completed. Total raw records created: %s",
            len(self.raw_data_ids),
        )

    def validate_raw_data(self):
        """
        The function iterates through a collection of records and checks if the count of raw data is
        less than a minimum threshold, and if so, it calls a validation function, otherwise it calls an
        """
        for rec in self:
            rec.locked = True
            rec.locked_reason = _("Validating data.")
            ceiling = self.JOB_QUEUE_BATCH_SIZE
            batches = math.ceil(len(rec.raw_data_ids) / ceiling)
            jobs = []
            for i in range(batches):
                start = i * ceiling
                end = min((i + 1) * ceiling, len(rec.raw_data_ids))
                jobs.append(rec.delayable(channel=_area_import_channel)._validate_raw_data(rec.raw_data_ids[start:end]))
            main_job = group(*jobs)
            main_job.on_done(rec.delayable(channel=_area_import_channel)._validate_mark_done())
            main_job.delay()

    def _validate_raw_data(self, raw_data_ids):
        """
        The function validates raw data and updates the state if there are no errors.
        """
        self.ensure_one()
        raw_data_ids.validate_raw_data()

    def _validate_mark_done(self):
        self.locked = False
        self.locked_reason = None
        self.ensure_one()
        if not self.env[_area_import_raw_model].search([("id", "in", self.raw_data_ids.ids), ("state", "=", "Error")]):
            self.update(
                {
                    "state": self.VALIDATED,
                }
            )

    def fix_area_level_and_kind(self):
        for rec in self:
            rec.locked = True
            rec.locked_reason = _("Fixing area level.")
            ceiling = self.JOB_QUEUE_BATCH_SIZE
            batches = math.ceil(len(rec.raw_data_ids) / ceiling)
            jobs = []
            for i in range(batches):
                start = i * ceiling
                end = min((i + 1) * ceiling, len(rec.raw_data_ids))
                jobs.append(
                    rec.delayable(channel=_area_import_channel)._fix_area_level_and_kind(rec.raw_data_ids[start:end])
                )
            main_job = group(*jobs)
            main_job.on_done(rec.delayable(channel=_area_import_channel)._async_mark_done())
            main_job.delay()

    def _fix_area_level_and_kind(self, raw_data_ids):
        """
        The function `fix_area_level_and_kind` fixes the area level of the raw data.
        """
        self.ensure_one()
        raw_data_ids.fix_area_level_and_kind()

    def _async_mark_done(self, function_mark_done=None):
        """
        The function `_async_mark_done` unlocks a resource by setting the `locked` attribute to `False`
        and clearing the `locked_reason` attribute.
        """
        self.ensure_one()

        self.locked = False
        self.locked_reason = None

        if function_mark_done:
            getattr(self, function_mark_done)()

    def save_to_area(self):
        """
        The function saves data to an area, either synchronously or asynchronously depending on the
        number of raw data records.
        """
        for rec in self:
            rec.locked = True
            rec.locked_reason = _("Importing data.")
            rec._async_recursive_save_to_area(rec.raw_data_ids)

    def _async_recursive_save_to_area(self, raw_data_ids):
        """
        This is to ensure that the function `_save_to_area` is called recursively and in order until all raw data
        is saved to the area.
        """
        self.ensure_one()
        jobs = []
        ceiling = self.JOB_QUEUE_BATCH_SIZE
        jobs.append(self.delayable(channel=_area_import_channel)._save_to_area(raw_data_ids[:ceiling]))
        main_job = group(*jobs)
        count = len(raw_data_ids)
        if count <= ceiling:
            main_job.on_done(self.delayable(channel=_area_import_channel)._save_to_area_mark_done())
        else:
            main_job.on_done(
                self.delayable(channel=_area_import_channel)._async_recursive_save_to_area(raw_data_ids[ceiling:])
            )
        main_job.delay()

    def _save_to_area(self, raw_data_ids):
        """
        The function saves raw data to an area and updates the state to "DONE".
        """
        self.ensure_one()

        raw_data_ids.save_to_area()

    def _save_to_area_mark_done(self):
        self.ensure_one()
        self.locked = False
        self.locked_reason = None
        if not self.env[_area_import_raw_model].search(
            [("id", "in", self.raw_data_ids.ids), ("state", "=", "Validated")]
        ):
            self.update(
                {
                    "state": self.DONE,
                }
            )

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
    _name = _area_import_raw_model
    _description = "Area Import Raw Data"
    _order = "level"
    _area_model = "spp.area"

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

    STATE_ORDER_STATE = {
        ERROR: 0,
        NEW: 1,
        VALIDATED: 2,
        UPDATED: 3,
        POSTED: 4,
    }

    area_import_id = fields.Many2one("spp.area.import", "Area Import", required=True)
    admin_name = fields.Char(translate=True)
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
    state_order = fields.Integer(
        compute="_compute_state_order",
        store=True,
    )
    area_id = fields.Many2one(_area_model, "Area", readonly=True)

    @api.depends("state")
    def _compute_state_order(self):
        for rec in self:
            rec.state_order = self.STATE_ORDER_STATE[rec.state]

    def check_errors(self):
        self.ensure_one()
        errors = []
        if not self.admin_name or not self.admin_code:
            errors.append(_("Name and Code of area is required."))

        if self.area_sqkm:
            try:
                float(self.area_sqkm)
            except ValueError:
                errors.append(_("AREA_SQKM should be numerical."))

        if self.level == 0 and (self.parent_name or self.parent_code):
            errors.append(_("Level 0 area should not have a parent name and parent code."))

        if self.level != 0 and (not self.parent_name or not self.parent_code):
            errors.append(_("Level 1 and above area should have a parent name and parent code."))
        return errors

    def validate_raw_data(self):
        for rec in self:
            errors = rec.check_errors()

            if errors:
                state = self.ERROR
                remarks = "\n".join(errors)
            else:
                state = self.VALIDATED
                remarks = "No Error"

            rec.write(
                {
                    "remarks": remarks,
                    "state": state,
                }
            )

    def get_area_vals(self):
        self.ensure_one()

        parent_id = None
        if self.parent_name and self.parent_code:
            parent_id = (
                self.env[self._area_model]
                .search(
                    [
                        ("code", "=", self.parent_code),
                    ],
                    limit=1,
                )
                .id
            )

        area_sqkm = self.area_sqkm

        try:
            area_sqkm = float(area_sqkm)
        except ValueError:
            area_sqkm = 0.0

        return {
            "parent_id": parent_id,
            "draft_name": self.admin_name,
            "code": self.admin_code,
            "area_sqkm": area_sqkm,
            "kind": self.env.ref("spp_area_base.admin_area_kind").id,
        }

    def save_to_area(self):
        """
        The function saves data to the "spp.area" model in the database, updating existing records if
        they exist and creating new records if they don't.
        """
        active_languages = self.env[_res_lang_model].search([("active", "=", True)])
        for rec in self:
            area_vals = rec.get_area_vals()
            if area_id := self.env[self._area_model].search([("code", "=", rec.admin_code)]):
                state = self.UPDATED
                area_id.update(area_vals)
            else:
                state = self.POSTED
                area_id = self.env[self._area_model].create(area_vals)

            for lang in active_languages:
                area_id.with_context(lang=lang.code).write(
                    {
                        "draft_name": rec.with_context(lang=lang.code).admin_name,
                    }
                )
                # Commenting out the compute_name and compute_complete_name
                # to lessen the load on the server, as this will be called when the area is saved with draft_name
                # area_id.with_context(lang=lang.code)._compute_name()
                # area_id.with_context(lang=lang.code)._compute_complete_name()

            rec.update(
                {
                    "state": state,
                    "remarks": "Successfully save to Area",
                    "area_id": area_id.id,
                }
            )

    def fix_area_level_and_kind(self):
        for rec in self:
            if rec.area_id and (rec.area_id.area_level != rec.level or not rec.area_id.kind):
                parent_id = None
                if rec.parent_name and rec.parent_code:
                    parent_id = (
                        self.env[self._area_model]
                        .search(
                            [
                                ("code", "=", rec.parent_code),
                            ],
                            limit=1,
                        )
                        .id
                    )
                rec.area_id.update(
                    {
                        "kind": rec.env.ref("spp_area_base.admin_area_kind").id,
                        "parent_id": parent_id,
                    }
                )


# JSON File Storage Model
class OpenSPPAreaImportJSON(models.Model):
    _name = "spp.area.import.json"
    _description = "Area Import JSON Files"
    _order = "batch_number"

    area_import_id = fields.Many2one("spp.area.import", "Area Import", required=True, ondelete="cascade")
    batch_number = fields.Integer("Batch Number", required=True)
    json_file = fields.Binary("JSON File", required=True)
    json_file_name = fields.Char("JSON File Name")
    row_count = fields.Integer("Row Count", help="Number of rows in this JSON file")
    file_size = fields.Integer("File Size (bytes)", help="Size of the JSON file in bytes")
