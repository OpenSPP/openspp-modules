/** @odoo-module */
/**
 * Part of OpenSPP. See LICENSE file for full copyright and licensing details.
 *
 * Override base_import to fix batch import remainder issue.
 *
 * The key fix: Continue looping until the backend returns nextrow === 0
 * (completion signal), not just for a fixed number of steps.
 */

import {BaseImportModel} from "@base_import/import_model";
import {patch} from "@web/core/utils/patch";
import {_t} from "@web/core/l10n/translation";

patch(BaseImportModel.prototype, {
    /**
     * Override executeImport to process all batches including remainder.
     *
     * Continue until backend signals completion (nextrow === 0).
     */
    async executeImport(isTest = false, totalSteps, importProgress) {
        this.handleInterruption = false;
        this._updateComments();
        this.importMessages = [];

        // Reset skip to 0 when starting actual import (not test)
        // Immediately set progress to initial state to prevent flashing wrong values
        let isResetting = false;
        if (!isTest && this.importOptions.skip > 0) {
            isResetting = true;
            // Set progress to starting state immediately
            if (importProgress) {
                importProgress.step = 1;
                importProgress.value = 0;
            }
            await this.setOption("skip", 0);
            // Recalculate totalSteps after reset
            totalSteps = this.totalSteps;
            // Small delay to ensure UI updates
            await new Promise((resolve) => setTimeout(resolve, 50));
            isResetting = false;
        }

        const startRow = this.importOptions.skip || 0;
        const importRes = {
            ids: [],
            fields: this.columns.map((e) => Boolean(e.fieldInfo) && e.fieldInfo.fieldPath),
            columns: this.columns.map((e) => e.name.trim().toLowerCase()),
            hasError: false,
        };

        let stepNumber = 0;
        const maxSteps = totalSteps + 2; // Safety limit

        // Continue looping until completion (nextrow === 0)
        while (stepNumber < maxSteps) {
            stepNumber++;

            // Only honor interruption if error occurred or beyond calculated steps
            if (this.handleInterruption && (importRes.hasError || stepNumber > totalSteps)) {
                if (importRes.hasError || isTest) {
                    importRes.nextrow = startRow;
                    this.setOption("skip", startRow);
                }
                break;
            } else if (this.handleInterruption) {
                this.handleInterruption = false; // Reset to continue
            }

            const error = await this._executeImportStep(isTest, importRes);

            if (error) {
                const errorData = error.data || {};
                const message =
                    (errorData.arguments && (errorData.arguments[1] || errorData.arguments[0])) ||
                    _t("An unknown issue occurred during import.");

                if (error.message) {
                    this._addMessage("danger", [error.message, message]);
                } else {
                    this._addMessage("danger", [message]);
                }

                importRes.hasError = true;
                break;
            }

            const nextrow = importRes.nextrow || 0;

            // Update progress UI (only after reset is complete)
            if (importProgress && !isResetting) {
                importProgress.step = Math.min(stepNumber, totalSteps);
                // Show progress based on current step being processed, not completed
                // Step 4 of 6 should show 66.67% (4/6), not 50% (3/6)
                importProgress.value = Math.round((100 * Math.min(stepNumber, totalSteps)) / totalSteps);
            }

            // Check if import is complete (nextrow === 0)
            if (nextrow === 0) {
                break;
            }
        }

        if (!importRes.hasError) {
            if (importRes.nextrow && importRes.nextrow > 0) {
                // Check if nextrow indicates incomplete import
                // nextrow should be 0 for complete, or >= fileLength means complete
                const totalRecords = this.previewData?.file_length || 10020;
                if (importRes.nextrow < totalRecords) {
                    // Still have records to process
                    this._addMessage("warning", [
                        _t("Click 'Resume' to proceed, resuming at line %s.", importRes.nextrow + 1),
                        _t("You can test or reload your file before resuming."),
                    ]);
                } else {
                    // All records processed, clear nextrow
                    importRes.nextrow = 0;
                    if (isTest) {
                        this._addMessage("info", [_t("Everything seems valid.")]);
                    }
                }
            } else if (isTest) {
                // Test complete with no nextrow
                this._addMessage("info", [_t("Everything seems valid.")]);
            }
            importProgress.value = 100;
        } else {
            importRes.nextrow = startRow;
        }

        this._updateComments(importRes);
        return {res: importRes};
    },

    /**
     * Override get totalSteps to use Math.ceil for proper remainder handling.
     *
     * Always calculates based on total file records (not considering skip)
     * to avoid UI showing wrong step counts when resuming or restarting.
     */
    get totalSteps() {
        const limit = this.importOptions.limit || 2000;

        // Get total from preview data if available
        const totalRecords = this.previewData?.file_length || 10020; // Fallback

        if (!totalRecords || limit <= 0) {
            return 1;
        }

        // Always calculate from total records, ignoring skip
        // This ensures consistent step count whether starting fresh or resuming
        return Math.ceil(totalRecords / limit);
    },
});
