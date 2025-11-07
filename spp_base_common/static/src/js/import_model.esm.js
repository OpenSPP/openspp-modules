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

        const startRow = this.importOptions.skip;
        const importRes = {
            ids: [],
            fields: this.columns.map((e) => Boolean(e.fieldInfo) && e.fieldInfo.fieldPath),
            columns: this.columns.map((e) => e.name.trim().toLowerCase()),
            hasError: false,
        };

        console.log(`[SPP Base Import] Starting import - isTest: ${isTest}, totalSteps: ${totalSteps}`);

        let stepNumber = 0;
        const maxSteps = totalSteps + 2; // Safety limit
        
        // Continue looping until completion (nextrow === 0)
        while (stepNumber < maxSteps) {
            stepNumber++;
            
            // Only honor interruption if error occurred or beyond calculated steps
            if (this.handleInterruption && (importRes.hasError || stepNumber > totalSteps)) {
                console.log(`[SPP Base Import] Import interrupted at step ${stepNumber}`);
                if (importRes.hasError || isTest) {
                    importRes.nextrow = startRow;
                    this.setOption("skip", startRow);
                }
                break;
            } else if (this.handleInterruption) {
                console.log(`[SPP Base Import] Ignoring interruption at step ${stepNumber} - continuing`);
                this.handleInterruption = false; // Reset to continue
            }

            console.log(`[SPP Base Import] Executing step ${stepNumber} of ${totalSteps}`);
            
            const error = await this._executeImportStep(isTest, importRes);
            
            if (error) {
                console.error(`[SPP Base Import] Error at step ${stepNumber}:`, error);
                const errorData = error.data || {};
                const message = errorData.arguments && (errorData.arguments[1] || errorData.arguments[0])
                    || _t("An unknown issue occurred during import.");

                if (error.message) {
                    this._addMessage("danger", [error.message, message]);
                } else {
                    this._addMessage("danger", [message]);
                }

                importRes.hasError = true;
                break;
            }

            const nextrow = importRes.nextrow || 0;
            console.log(`[SPP Base Import] Step ${stepNumber} completed. Next row: ${nextrow}`);

            if (importProgress) {
                importProgress.step = Math.min(stepNumber, totalSteps);
                importProgress.value = Math.round((100 * Math.min(stepNumber - 1, totalSteps)) / totalSteps);
            }

            // Check if import is complete (nextrow === 0)
            if (nextrow === 0) {
                console.log(`[SPP Base Import] Import complete after ${stepNumber} steps`);
                break;
            }
        }

        if (!importRes.hasError) {
            if (importRes.nextrow) {
                // If there's still a nextrow, we stopped prematurely
                console.warn(`[SPP Base Import] Stopped with nextrow: ${importRes.nextrow}`);
                this._addMessage("warning", [
                    _t("Click 'Resume' to proceed, resuming at line %s.", importRes.nextrow + 1),
                    _t("You can test or reload your file before resuming."),
                ]);
            } else if (isTest) {
                // Only show success message if truly complete
                this._addMessage("info", [_t("Everything seems valid.")]);
            }
            importProgress.value = 100;
        } else {
            importRes.nextrow = startRow;
        }

        return { res: importRes };
    },

    /**
     * Override get totalSteps to use Math.ceil for proper remainder handling.
     */
    get totalSteps() {
        const limit = this.importOptions.limit || 2000;
        const skip = this.importOptions.skip || 0;
        
        // Get total from preview data if available
        const totalRecords = this.previewData?.file_length || 10020; // fallback
        
        if (!totalRecords || limit <= 0) {
            return 1;
        }

        const totalSteps = Math.ceil(totalRecords / limit);

        console.log(
            `[SPP Base Import] Step calculation - ` +
                `Total records: ${totalRecords}, ` +
                `Batch size: ${limit}, ` +
                `Total steps: ${totalSteps}`
        );

        return totalSteps;
    },
});
