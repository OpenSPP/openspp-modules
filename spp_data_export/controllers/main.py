import json

from odoo import _, http
from odoo.exceptions import ValidationError
from odoo.http import request

from odoo.addons.web.controllers.export import ExcelExport

EXCEL_ROW_LIMIT = 1_048_576


class SppExport(ExcelExport):
    @http.route("/web/export/xlsx", type="http", auth="user")
    def index(self, data):
        """
        In case too many records are selected to export, Odoo server will try to load all records then create
        Excel report. At this time, due to timeout error, the Promise won't return and will raising an weird
        error stack.

        This function override the original function, to raise a properly error if the records count is more than
        the limitation of Excel report, saving the time to generate report and fail.
        """
        json_data = json.loads(data)
        if not json_data.get("ids"):
            domain = json_data.get("domain")
            model = json_data.get("model")
            number_of_records = request.env[model].sudo().search_count(domain)
            if number_of_records >= EXCEL_ROW_LIMIT:
                raise ValidationError(
                    _(
                        "The number of record surpasses the limitation of Excel 2007-2013 (.xlsx) format "
                        "[%(number_of_records)s records >= limit %(limit)s]. Please consider splitting the export."
                    )
                    % {
                        "number_of_records": number_of_records,
                        "limit": EXCEL_ROW_LIMIT,
                    }
                )
        return super().index(data)
