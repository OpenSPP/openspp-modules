/** @odoo-module **/
/**
 * Part of OpenSPP. See LICENSE file for full copyright and licensing details.
 *
 * Override legacy base_import to fix batch import remainder issue.
 *
 * This handles the legacy implementation for backward compatibility.
 */

odoo.define("spp_base_common.ImportActionLegacy", function (require) {
    // Try to require base_import, return gracefully if not available
    let DataImport;
    try {
        DataImport = require("base_import.import");
    } catch (e) {
        console.log("[SPP Base Import Legacy] base_import.import not available, skipping legacy patch");
        return;
    }
    
    if (!DataImport) {
        console.log("[SPP Base Import Legacy] DataImport not found, skipping legacy patch");
        return;
    }

    /**
     * Override the call_import method to fix totalSteps calculation.
     *
     * The original implementation uses Math.floor() + 1 which incorrectly
     * adds an extra step even when there's no remainder.
     */
    DataImport.include({
        call_import: function (kwargs) {
            const fields = this.$("input.oe_import_match_field")
                .map(function (index, el) {
                    return $(el).select2("val") || false;
                })
                .get();
            const columns = this.$(".o_import_header_name")
                .map(function () {
                    return $(this).text().trim().toLowerCase() || false;
                })
                .get();

            const tracking_disable =
                "tracking_disable" in kwargs
                    ? kwargs.tracking_disable
                    : !this.$("#oe_import_tracking").prop("checked");
            delete kwargs.tracking_disable;
            kwargs.context = _.extend({}, this.parent_context, {tracking_disable: tracking_disable});

            this.importStartTime = Date.now();
            this.stopImport = false;
            const skipRows = parseInt(this.$("#oe_import_row_start").val()) || 0;
            this.totalToImport = this.fileLength - skipRows;
            this.batchSize = parseInt(this.$("#oe_import_batch_limit").val() || 0);
            const isBatch = this.batchSize !== 0 && this.totalToImport > this.batchSize;

            // FIX: Use Math.ceil instead of Math.floor + 1
            // This properly handles remainder batches:
            // - 40100 / 2000 = 20.05 → ceil(20.05) = 21 ✓
            // - 40000 / 2000 = 20.0 → ceil(20.0) = 20 ✓
            // For resume: calculate based on fileLength, not remaining records
            const totalRecords = this.fileLength;
            const totalSteps = isBatch ? Math.ceil(totalRecords / this.batchSize) : 1;

            console.log(
                "[SPP Base Import Legacy] Batch calculation - " +
                    "Total records: " +
                    totalRecords +
                    " (" +
                    this.totalToImport +
                    " remaining + " +
                    skipRows +
                    " skipped), " +
                    "Batch size: " +
                    this.batchSize +
                    ", " +
                    "Total steps: " +
                    totalSteps
            );

            this.currentBatchNumber = 1;

            $.blockUI({
                message: QWeb.render("base_import.progressDialog", {
                    importMode: kwargs.dryrun ? _t("Testing") : _t("Importing"),
                    isBatch: isBatch,
                    totalSteps: totalSteps,
                }),
            });
            $(document.body).addClass("o_ui_blocked");

            $(".o_import_progress_dialog")
                .find(".o_progress_stop_import")
                .on("click", this._onStopImport.bind(this));

            const opts = this.import_options();

            return this._batchedImport(opts, [this.id, fields, columns], kwargs, 0, totalSteps);
        },
    });

    return DataImport;
});
