# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import base64
import logging
from io import BytesIO

from xlrd import open_workbook

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class OpenSPPAreaImport(models.Model):
    _name = "spp.area.import"
    _description = "Areas Import Table"

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

    @api.onchange("excel_file")
    def excel_file_change(self):
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

    @api.depends("raw_data_ids")
    def _compute_get_total_rows(self):
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
            rec.update({"state": "Cancelled"})

    def import_data(self):  # noqa: C901
        _logger.info("Area Import: Started: %s" % fields.Datetime.now())
        for rec in self:
            _logger.info("Area Import: Loading Excel File: %s" % fields.Datetime.now())
            try:
                inputx = BytesIO()
                inputx.write(base64.decodebytes(rec.excel_file))
                book = open_workbook(file_contents=inputx.getvalue())
            except TypeError as e:
                raise ValidationError(_("ERROR: {}").format(e))  # noqa: C901, B904
            sheet = book.sheets()[0]
            vals = []
            _logger.info("Area Import: Parsing Excel File: %s" % fields.Datetime.now())

            columns = []

            mainvals = {}
            max_cols = None
            for row in range(sheet.nrows):
                if row == 0:  # Ignore First Row containing column headings
                    for col in range(sheet.ncols):
                        col_name = sheet.cell(0, col).value
                        if col_name.find("Name") >= 0:
                            maxcolsstr = ""
                            if col_name.find("admin") >= 0:
                                maxcolsstr = col_name.strip("admin").replace("Name", "")
                            elif col_name.find("Area") >= 0:
                                maxcolsstr = col_name.strip("Area").replace("Name", "")
                            maxcols_name_length = len(maxcolsstr)
                            if maxcols_name_length == 5 or maxcols_name_length == 4:
                                maxcolsstr = maxcolsstr[:-3]
                                maxcolsstr = maxcolsstr.replace("_", "")
                            try:
                                max_cols = int(maxcolsstr)
                                break
                            except Exception:
                                max_cols = None
                else:
                    if max_cols:
                        xcols = max_cols
                        while xcols >= 0:

                            admin_code = None
                            admin_name = None
                            admin_ref = None
                            admin_alt1 = None
                            admin_alt2 = None
                            admin_kind = None
                            state = "Validated"
                            errctr = 0
                            remarks = ""
                            # Loop through the columns
                            lang = {}
                            Languages = self.env["res.lang"].search(
                                [("active", "=", True)]
                            )
                            for col in range(sheet.ncols):

                                # Get the column value
                                col_value = sheet.cell(row, col).value
                                if col_value == "<Null>":
                                    col_value = ""

                                # Determine the column name based on First Row rowIndex(0), columnIndex(col)
                                col_name = sheet.cell(0, col).value
                                if (
                                    col_name.find(str(xcols) + "Code") >= 0
                                    or col_name.find(str(xcols) + "Pcode") >= 0
                                ):
                                    admin_code = col_value
                                elif col_name.find(str(xcols) + "Name") >= 0:
                                    if not admin_name:
                                        admin_name = col_value
                                        if not col_value:
                                            errctr += 1
                                            state = "Error"
                                            remarks += (
                                                str(errctr)
                                                + ".) Name cannot be blank; "
                                            )

                                    for Lang in Languages:
                                        if (
                                            col_name.find(
                                                str(xcols) + "Name_" + Lang.iso_code
                                            )
                                            >= 0
                                        ):
                                            lang.update(
                                                {
                                                    Lang.iso_code: {
                                                        "name": col_value,
                                                        "lang_id": Lang.id,
                                                        "iso_code": Lang.iso_code,
                                                    }
                                                }
                                            )

                                elif col_name.find(str(xcols) + "Ref") >= 0:
                                    admin_ref = col_value
                                elif col_name.find(str(xcols) + "AltName1") >= 0:
                                    admin_alt1 = col_value
                                elif col_name.find(str(xcols) + "AltName2") >= 0:
                                    admin_alt2 = col_value
                                elif col_name.find(str(xcols) + "Kind") >= 0:
                                    admin_kind = col_value
                                _logger.info(
                                    "Area Masterlist Import: LANGUAGES: %s" % lang
                                )
                            lang_ids = []
                            for x in lang:
                                lang_ids.append([0, 0, lang[x]])

                            # Store values to columns
                            columns.append(
                                {
                                    "admin_name": admin_name,
                                    "admin_code": admin_code,
                                    "admin_ref": admin_ref,
                                    "admin_alt1": admin_alt1,
                                    "admin_alt2": admin_alt2,
                                    "admin_kind": admin_kind,
                                    "level": xcols,
                                    "remarks": remarks,
                                    "state": state,
                                    "row_index": row,
                                    "lang_ids": lang_ids,
                                }
                            )

                            xcols -= 1

            for val in columns:
                vals.append([0, 0, val])

            # raise Warning('Debug: %s' % vals)
            _logger.info(
                "Area Masterlist Import: Updating Record: %s" % fields.Datetime.now()
            )
            mainvals.update(
                {
                    "date_imported": fields.Datetime.now(),
                    "import_id": self.env.user,
                    "date_validated": fields.Datetime.now(),
                    "validate_id": self.env.user,
                    "state": "Imported",
                    "raw_data_ids": vals,
                }
            )
            rec.update(mainvals)

            _logger.info(
                "Area Masterlist Import: Completed: %s" % fields.Datetime.now()
            )

    def save_to_area(self):
        for rec in self:
            parent_id = None
            for raw in rec.raw_data_ids:
                if raw.state == "Validated":
                    if raw.admin_name:
                        area_kind = None
                        area_kind_id = None
                        if raw.admin_kind:
                            area_kind = self.env["spp.area.kind"].search(
                                [("name", "=", raw.admin_kind)]
                            )
                            if not area_kind:
                                vals = [{"name": raw.admin_kind}]
                                area_kind = self.env["spp.area.kind"].create(vals)
                                area_kind_id = area_kind[0].id
                        if raw.level == 0:
                            new_vals = {
                                "name": raw.admin_name or False,
                                "code": raw.admin_code or False,
                                "altnames": raw.admin_alt1 or raw.admin_alt2 or False,
                                "level": raw.level or False,
                                "kind": area_kind_id or False,
                            }
                        else:
                            new_vals = {
                                "parent_id": parent_id,
                                "name": raw.admin_name or False,
                                "code": raw.admin_code or False,
                                "altnames": raw.admin_alt1 or raw.admin_alt2 or False,
                                "level": raw.level or False,
                                "kind": area_kind_id or False,
                            }
                        # Check if Area already Exist
                        curr_area = self.env["spp.area"].search(
                            [
                                ("name", "=", raw.admin_name),
                                ("code", "=", raw.admin_code),
                            ]
                        )

                        if not curr_area:
                            area_id = self.env["spp.area"].create(new_vals)
                            parent_id = area_id.id
                            raw.update({"state": "Posted"})
                        else:
                            area_id = curr_area[0].update(new_vals)
                            parent_id = curr_area[0].id
                            raw.update({"state": "Updated"})
                        for lang in raw.lang_ids:
                            vals_list = []
                            trans_name = lang.name
                            iso_code = lang.lang_id.code
                            vals_list.append(
                                {
                                    "name": "spp.area,name",
                                    "lang": iso_code,
                                    "res_id": parent_id,
                                    "src": raw.admin_name,
                                    "value": trans_name,
                                    "state": "translated",
                                    "type": "model",
                                }
                            )
                            self.env["ir.translation"]._update_translations(vals_list)
                        rec.update({"state": "Done"})
                    else:
                        raw.update({"state": "Error"})

                else:
                    raw.update({"state": "Error", "remarks": "Incomplete information!"})


# Assets Import Raw Data
class OpenSPPAreaImportActivities(models.Model):
    _name = "spp.area.import.raw"
    _description = "Area Import Raw Data"
    _order = "row_index, level"

    area_import_id = fields.Many2one("spp.area.import", "Area Import", required=True)
    admin_name = fields.Char()
    admin_code = fields.Char()
    admin_alt1 = fields.Char()
    admin_alt2 = fields.Char()
    admin_ref = fields.Char()
    admin_kind = fields.Char()
    level = fields.Integer()
    row_index = fields.Integer()
    lang_ids = fields.One2many("spp.area.import.lang", "raw_id", "Languages")
    remarks = fields.Text("Remarks/Errors")
    state = fields.Selection(
        [
            ("New", "New"),
            ("Validated", "Validated"),
            ("Error", "Error"),
            ("Updated", "Updated"),
            ("Posted", "Posted"),
        ],
        "Status",
        readonly=True,
        default="New",
    )


class OpenSPPAreaImportRawLanguages(models.Model):
    _name = "spp.area.import.lang"
    _description = "Area Import Raw Data Languages"

    name = fields.Char("Translate Name")
    raw_id = fields.Many2one("spp.area.import.raw", "Area Raw ID")
    lang_id = fields.Many2one("res.lang", "Languages")

    iso_code = fields.Char("ISO Code")
