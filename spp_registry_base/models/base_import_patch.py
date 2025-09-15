from odoo import models


class BaseImportPatch(models.TransientModel):
    _inherit = "base_import.import"

    def execute_import(self, fields, columns, options, dryrun=False):
        """
        Override to process all batches, including the remainder.
        """
        batch_size = options.get("limit", 2000)
        file_length, _ = self._read_file(options)
        imported_ids = []
        messages = []
        results = {}

        for skip in range(0, file_length, batch_size):
            batch_options = dict(options)
            batch_options["skip"] = skip
            batch_options["limit"] = batch_size
            result = super().execute_import(fields, columns, batch_options, dryrun=dryrun)
            imported_ids.extend(result.get("ids", []))
            messages.extend(result.get("messages", []))
            results = result

        results["ids"] = imported_ids
        results["messages"] = messages
        return results
