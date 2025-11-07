/** @odoo-module */
/**
 * Part of OpenSPP. See LICENSE file for full copyright and licensing details.
 *
 * Override base_import to fix batch import remainder issue.
 *
 * Ensures proper step calculation and that remainder batches are processed
 * automatically without stopping. The loop continues until nextrow === 0
 * which signals completion, not just for a fixed number of steps.
 */

import {BaseImportModel} from "@base_import/import_model";
import {patch} from "@web/core/utils/patch";
import {_t} from "@web/core/l10n/translation";

patch(BaseImportModel.prototype, {
    /**
     * Override executeImport to ensure all batches including remainder execute.
     * 
     * The loop continues until the backend returns nextrow: 0, which signals
     * that all records have been processed.
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

        console.log(`[SPP Base Import] Starting import - isTest: ${isTest}, totalSteps: ${totalSteps}, startRow: ${startRow}, fileLength: ${this.fileLength}`);

        let stepNumber = 0;
        const maxSteps = totalSteps + 2; // Safety limit: allow 2 extra steps beyond calculated
        
        // Continue looping until backend signals completion (nextrow === 0) or error
        while (stepNumber < maxSteps) {
            stepNumber++;
            
            if (this.handleInterruption) {
                console.log(`[SPP Base Import] Import interrupted at step ${stepNumber}`);
                if (importRes.hasError || isTest) {
                    importRes.nextrow = startRow;
                    this.setOption("skip", startRow);
                }
                break;
            }

            console.log(`[SPP Base Import] Executing step ${stepNumber}, skip: ${this.importOptions.skip}`);
            const error = await this._executeImportStep(isTest, importRes);
            
            if (error) {
                console.error(`[SPP Base Import] Error at step ${stepNumber}:`, error);
                const errorData = error.data || {};
                const message = errorData.arguments && (errorData.arguments[1] || errorData.arguments[0])
                    || _t("An unknown issue occurred during import (possibly lost connection, data limit exceeded or memory limits exceeded). Please retry in case the issue is transient. If the issue still occurs, try to split the file rather than import it at once.");

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

            // Check if import is complete (nextrow === 0 signals completion)
            if (nextrow === 0) {
                console.log(`[SPP Base Import] Import complete after ${stepNumber} steps`);
                break;
            }
        }

        if (stepNumber >= maxSteps) {
            console.warn(`[SPP Base Import] Reached maximum steps (${maxSteps}), stopping`);
        }

        if (!importRes.hasError) {
            importProgress.value = 100;
        }
        this._updateComments(importRes);
        return {
            messages: this.importMessages.map((m) => m.message),
        };
    },

    /**
     * Override get totalSteps to ensure proper calculation including remainder.
     */
    get totalSteps() {
        const limit = this.importOptions.limit || 2000;
        
        if (!this.fileLength || limit <= 0) {
            return 1;
        }

        // Calculate total steps based on file length
        const totalSteps = Math.ceil(this.fileLength / limit);

        console.log(
            `[SPP Base Import] Step calculation - ` +
                `File records: ${this.fileLength}, ` +
                `Batch size: ${limit}, ` +
                `Total steps: ${totalSteps}`
        );

        return totalSteps;
    },
});
