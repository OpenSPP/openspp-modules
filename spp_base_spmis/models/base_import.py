# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging
import math

from odoo import models

_logger = logging.getLogger(__name__)


class SPPMISBaseImport(models.TransientModel):
    """
    Override base_import to fix batch import remainder issue.

    The goal is to ensure that when calculating total steps for batch imports,
    the remainder is included. For example, 40100 records with batch size 2000
    should create 21 steps (20 batches of 2000 + 1 batch of 100), not 20 steps.
    """

    _inherit = "base_import.import"

    def _get_batch_info(self, total_records, batch_size):
        """
        Calculate batch information including remainder.

        Args:
            total_records: Total number of records to import
            batch_size: Size of each batch

        Returns:
            dict: {
                'total_steps': Total number of batches including remainder,
                'full_batches': Number of full batches,
                'remainder': Number of records in the last batch (if any)
            }
        """
        if batch_size <= 0 or total_records <= 0:
            return {"total_steps": 0, "full_batches": 0, "remainder": 0}

        # Calculate total steps using ceiling division
        # This ensures remainder is counted as a step
        total_steps = math.ceil(total_records / batch_size)
        full_batches = total_records // batch_size
        remainder = total_records % batch_size

        _logger.info(
            "Batch calculation - Total records: %s, Batch size: %s, "
            "Total steps: %s, Full batches: %s, Remainder: %s",
            total_records,
            batch_size,
            total_steps,
            full_batches,
            remainder,
        )

        return {
            "total_steps": total_steps,
            "full_batches": full_batches,
            "remainder": remainder,
        }

    def execute_import(self, fields, columns, options, dryrun=False):
        """
        Override execute_import to properly handle batch calculations
        for test imports (dryrun).

        When testing imports with batching, this ensures the test considers
        all batches including any remainder records.
        """
        # Get batch size from options (default is 0 for no batching)
        batch_size = options.get("limit", 0)

        # If this is a test import (dryrun) and batching is enabled
        if dryrun and batch_size > 0:
            # Convert import data first to get total record count
            try:
                # Check if the parent module has _convert_import_data method
                if hasattr(super(), "_convert_import_data"):
                    input_file_data, import_fields = self._convert_import_data(fields, options)
                else:
                    # Fallback to standard data loading
                    input_file_data = self._read_file(options)

                total_records = len(input_file_data)

                # Calculate batch information
                batch_info = self._get_batch_info(total_records, batch_size)

                # Add batch information to options for frontend
                options["_batch_info"] = batch_info

                _logger.info(
                    "Test import - Model: %s, Total records: %s, "
                    "Batch size: %s, Total steps (including remainder): %s",
                    self.res_model,
                    total_records,
                    batch_size,
                    batch_info["total_steps"],
                )

            except Exception as e:
                _logger.warning("Could not calculate batch info during test import: %s", str(e))

        # Call parent execute_import
        result = super().execute_import(fields, columns, options, dryrun=dryrun)

        # Add batch info to result for frontend consumption
        if dryrun and batch_size > 0 and options.get("_batch_info"):
            if isinstance(result, dict):
                result["batch_info"] = options["_batch_info"]

        return result

    def _read_file(self, options):
        """
        Helper method to read and parse the import file.

        Returns:
            list: Parsed data rows
        """
        # This is a simplified version - adjust based on your actual file reading logic
        if not self.file:
            return []

        # Use Odoo's built-in CSV parsing

        import base64
        import csv
        from io import StringIO

        decoded_data = base64.b64decode(self.file)
        encoding = options.get("encoding", "utf-8")

        try:
            data_string = decoded_data.decode(encoding)
        except UnicodeDecodeError:
            data_string = decoded_data.decode("latin-1")

        # Parse CSV
        separator = options.get("separator", ",")
        quoting = options.get("quoting", '"')

        reader = csv.reader(StringIO(data_string), delimiter=separator, quotechar=quoting)

        data = list(reader)

        # Remove header if present
        if options.get("headers", False):
            data = data[1:]

        return data
