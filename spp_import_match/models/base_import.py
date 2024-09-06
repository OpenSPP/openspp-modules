import base64
import csv
import logging
from io import BytesIO, StringIO, TextIOWrapper
from os.path import splitext

from odoo import _, api, models
from odoo.models import fix_import_export_id_paths

from odoo.addons.queue_job.exception import FailedJobError

_logger = logging.getLogger(__name__)
# options defined in base_import/import.js
OPT_HAS_HEADER = "headers"
OPT_SEPARATOR = "separator"
OPT_QUOTING = "quoting"
OPT_ENCODING = "encoding"
# options defined in base_import_async/import.js
OPT_USE_QUEUE = "use_queue"
OPT_CHUNK_SIZE = "chunk_size"
# option not available in UI, but usable from scripts
OPT_PRIORITY = "priority"

INIT_PRIORITY = 100
DEFAULT_CHUNK_SIZE = 100


class ImportValidationError(Exception):
    """
    This class is made to correctly format all the different error types that
    can occur during the pre-validation of the import that is made before
    calling the data loading itself. The Error data structure is meant to copy
    the one of the errors raised during the data loading. It simplifies the
    error management at client side as all errors can be treated the same way.

    This exception is typically raised when there is an error during data
    parsing (image, int, dates, etc..) or if the user did not select at least
    one field to map with a column.
    """

    def __init__(self, message, **kwargs):
        super().__init__(message)
        self.type = kwargs.get("error_type", "error")
        self.message = message
        self.record = False
        self.not_matching_error = True
        self.field_path = [kwargs["field"]] if kwargs.get("field") else False
        self.field_type = kwargs.get("field_type")


class SPPBaseImport(models.TransientModel):
    _inherit = "base_import.import"

    def execute_import(self, fields, columns, options, dryrun=False):
        try:
            input_file_data, import_fields = self._convert_import_data(fields, options)
            # Parse date and float field
            input_file_data = self._parse_import_data(input_file_data, import_fields, options)
        except ImportValidationError as error:
            return {"messages": [error.__dict__]}

        _logger.info(f"Started Import: {self.res_model} with rows {len(input_file_data)}")

        if dryrun and len(input_file_data) > 100:
            self._cr.execute("SAVEPOINT import")

            import_fields, merged_data = self._handle_multi_mapping(import_fields, input_file_data)

            if options.get("fallback_values"):
                merged_data = self._handle_fallback_values(import_fields, merged_data, options["fallback_values"])

            model = self.env[self.res_model].with_context(self.env.context)
            import_result = model.load(import_fields, merged_data[:1])

            self._cr.execute("ROLLBACK TO SAVEPOINT import")
            self.pool.clear_all_caches()
            self.pool.reset_changes()
            return import_result

        if dryrun or not len(input_file_data) > 100:
            # normal import
            _logger.info("Doing Normal Import")
            import_match_ids = options.get("import_match_ids", [])
            if import_match_ids:
                self = self.with_context(import_match_ids=import_match_ids)
            return super().execute_import(fields, columns, options, dryrun=dryrun)
        _logger.info("Started Asynchronous Import: %s" % self.res_model)
        # asynchronous import
        try:
            data, import_fields = self._convert_import_data(fields, options)
            # Parse date and float field
            data = self._parse_import_data(data, import_fields, options)
        except ValueError as e:
            return {"messages": [{"type": "error", "message": str(e), "record": False}]}

        # get the translated model name to build
        # a meaningful job description
        search_result = self.env["ir.model"].name_search(self.res_model, operator="=")
        if search_result:
            translated_model_name = search_result[0][1]
        else:
            translated_model_name = self._description
        description = _("Import {model_name} from file {file_name}").format(
            model_name=translated_model_name, file_name=self.file_name
        )
        attachment = self._create_csv_attachment(import_fields, data, options, self.file_name)
        delayed_job = self.with_delay(description=description)._split_file(
            model_name=self.res_model,
            translated_model_name=translated_model_name,
            attachment=attachment,
            options=options,
            split_context=self.env.context,
            file_name=self.file_name,
        )
        self._link_attachment_to_job(delayed_job, attachment)
        return {"async": True}

    def _link_attachment_to_job(self, delayed_job, attachment):
        queue_job = self.env["queue.job"].search([("uuid", "=", delayed_job.uuid)], limit=1)
        attachment.write({"res_model": "queue.job", "res_id": queue_job.id})

    @api.returns("ir.attachment")
    def _create_csv_attachment(self, fields, data, options, file_name):
        # write csv
        f = StringIO()
        writer = csv.writer(
            f,
            delimiter=str(options.get(OPT_SEPARATOR)) or ",",
            quotechar=str(options.get(OPT_QUOTING)),
        )
        encoding = options.get(OPT_ENCODING) or "utf-8"
        writer.writerow(fields)
        for row in data:
            writer.writerow(row)
        # create attachment
        datas = base64.encodebytes(f.getvalue().encode(encoding))
        attachment = self.env["ir.attachment"].create({"name": file_name, "datas": datas})
        return attachment

    def _read_csv_attachment(self, attachment, options):
        decoded_datas = base64.decodebytes(attachment.datas)
        encoding = options.get(OPT_ENCODING) or "utf-8"
        f = TextIOWrapper(BytesIO(decoded_datas), encoding=encoding)
        reader = csv.reader(
            f,
            delimiter=str(options.get(OPT_SEPARATOR)) or ",",
            quotechar=str(options.get(OPT_QUOTING)),
        )

        fields = next(reader)
        data = [row for row in reader]
        return fields, data

    @staticmethod
    def _extract_chunks(model_obj, fields, data, chunk_size):
        """Split the data on record boundaries, in chunks of minimum chunk_size"""
        fields = list(map(fix_import_export_id_paths, fields))
        row_from = 0
        for rows in model_obj._extract_records(fields, data):
            rows = rows[1]["rows"]
            if rows["to"] - row_from + 1 >= chunk_size:
                yield row_from, rows["to"]
                row_from = rows["to"] + 1
        if row_from < len(data):
            yield row_from, len(data) - 1

    def _split_file(
        self,
        model_name,
        translated_model_name,
        attachment,
        options,
        split_context,
        file_name="file.csv",
    ):
        """Split a CSV attachment in smaller import jobs"""
        model_obj = self.env[model_name]
        fields, data = self._read_csv_attachment(attachment, options)
        padding = len(str(len(data)))
        priority = options.get(OPT_PRIORITY, INIT_PRIORITY)
        if options.get(OPT_HAS_HEADER):
            header_offset = 1
        else:
            header_offset = 0
        chunk_size = options.get(OPT_CHUNK_SIZE) or DEFAULT_CHUNK_SIZE
        for row_from, row_to in self._extract_chunks(model_obj, fields, data, chunk_size):
            chunk = str(priority - INIT_PRIORITY).zfill(padding)
            description = _(
                "Import {model_name} from file {file_name} - #{chunk} - lines {row_from} to {row_to}"
            ).format(
                model_name=translated_model_name,
                file_name=file_name,
                chunk=chunk,
                row_from=row_from + 1 + header_offset,
                row_to=row_to + 1 + header_offset,
            )
            # create a CSV attachment and enqueue the job
            root, ext = splitext(file_name)
            attachment = self._create_csv_attachment(
                fields,
                data[row_from : row_to + 1],
                options,
                file_name=root + "-" + chunk + ext,
            )
            delayed_job = self.with_delay(description=description, priority=priority)._import_one_chunk(
                model_name=model_name, attachment=attachment, options=options, context=split_context
            )
            self._link_attachment_to_job(delayed_job, attachment)
            priority += 1

    def _import_one_chunk(self, model_name, attachment, options, context):
        model_obj = self.env[model_name].with_context(context)
        fields, data = self._read_csv_attachment(attachment, options)
        result = model_obj.load(fields, data)
        error_message = [message["message"] for message in result["messages"] if message["type"] == "error"]
        if error_message:
            raise FailedJobError("\n".join(error_message))
        return result
