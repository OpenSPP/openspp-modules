import logging

from odoo import models

LIMIT_FIELD = "limit"
_logger = logging.getLogger(__name__)


class BaseImportPatch(models.TransientModel):
    _inherit = "base_import.import"

    def execute_import(self, fields, columns, options, dryrun=False):
        """
        Override to include the remainder in batches for both 'Test' and 'Import'
        by using Odoo's stepping mechanism, preventing CPU timeouts on large files.
        """
        _logger.info("--- execute_import START ---")
        self.ensure_one()

        # Determine the current batch size and starting point.
        limit = options.get(LIMIT_FIELD, 2000)
        skip = options.get("skip", 0)

        # Process the current batch using the parent method.
        _logger.info("Calling super().execute_import with options: %s, dryrun: %s", options, dryrun)
        # This will either be a test (dryrun) or an actual import.
        results = super().execute_import(fields, columns, options, dryrun=dryrun)

        # Check if there are more records to process in subsequent batches.
        # We need to get the total file length, not just the current batch.
        # The 'skip' and 'limit' in options can affect the result of _read_file,
        # so we pass a clean options dict to get the total length.
        clean_options = {k: v for k, v in options.items() if k not in ("skip", LIMIT_FIELD)}
        file_length, _ = self._read_file(clean_options)

        # The base implementation returns an empty list for `ids` on dryrun,
        # so we rely on the number of messages to determine the processed count.
        processed_rows = len(results.get("ids", []) or results.get("messages", []))
        has_more = (skip + processed_rows) < file_length and processed_rows > 0
        _logger.info(
            "skip: %s, processed_rows: %s, file_length: %s, has_more: %s", skip, processed_rows, file_length, has_more
        )

        if has_more:
            # If more records exist, return an action to trigger the next step.
            # This works for both dryrun and actual import.
            # The JS client expects a simple dictionary with the next 'options'.
            next_action = {"options": {**options, "skip": skip + limit}}
            next_step = skip + limit
            if next_step > file_length:
                _logger.info("No More: Setting next_action with default_skip: 0")
                next_action = {"options": {**options, "skip": 0}}
                results["next_action"] = next_action
            else:
                _logger.info("HAS MORE: Setting next_action with default_skip: %s", skip + limit)
                results["next_action"] = next_action
        elif dryrun:
            # This is the final batch of a dryrun (Test).
            # We must return a next_action that explicitly resets the skip value
            # to 0. This tells the client to reset the UI for the real import.
            next_action = {"options": {**options, "skip": 0}}
            _logger.info("FINAL DRYRUN: Resetting next_action with default_skip: 0")
            results["next_action"] = next_action
        else:
            _logger.info("FINAL IMPORT or NO MORE: No next_action is set.")

        _logger.info("--- execute_import END ---")
        return results
