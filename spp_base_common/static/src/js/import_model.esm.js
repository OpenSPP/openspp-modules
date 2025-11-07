/** @odoo-module */
/**
 * Part of OpenSPP. See LICENSE file for full copyright and licensing details.
 *
 * Override base_import to fix batch import remainder issue.
 *
 * Ensures proper step calculation and that remainder batches are processed
 * automatically without stopping.
 */

import {BaseImportModel} from "@base_import/import_model";
import {patch} from "@web/core/utils/patch";
import {_t} from "@web/core/l10n/translation";

patch(BaseImportModel.prototype, {
    /**
     * Override executeImport to ensure all batches including remainder execute.
     * 
     * The loop continues until the backend signals completion (nextrow === 0)
     * or we've processed all records (nextrow >= fileLength).
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
        const maxSteps = totalSteps + 1; // Allow 1 extra step for safety
        
        // Continue looping until completion
        while (stepNumber < maxSteps) {
            stepNumber++;
            
            // Only honor interruption if there was an error or user explicitly stopped
            if (this.handleInterruption && (importRes.hasError || stepNumber > totalSteps)) {
                console.log(`[SPP Base Import] Import interrupted at step ${stepNumber} (hasError: ${importRes.hasError})`);
                if (importRes.hasError || isTest) {
                    importRes.nextrow = startRow;
                    this.setOption("skip", startRow);
                }
                break;
            } else if (this.handleInterruption) {
                console.log(`[SPP Base Import] Ignoring interruption at step ${stepNumber} - continuing to process remaining records`);
                this.handleInterruption = false; // Reset to continue
            }

            const currentSkip = this.importOptions.skip || 0;
            console.log(`[SPP Base Import] Executing step ${stepNumber}, skip: ${currentSkip}, remaining: ${this.fileLength - currentSkip}`);
            
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
            console.log(`[SPP Base Import] Step ${stepNumber} completed. Next row: ${nextrow}, fileLength: ${this.fileLength}`);

            if (importProgress) {
                importProgress.step = Math.min(stepNumber, totalSteps);
                importProgress.value = Math.round((100 * Math.min(stepNumber - 1, totalSteps)) / totalSteps);
            }

            // Check if import is complete:
            // - nextrow === 0 signals completion from backend
            // - nextrow >= fileLength means we've processed all records
            if (nextrow === 0 || nextrow >= this.fileLength) {
                console.log(`[SPP Base Import] Import complete after ${stepNumber} steps (nextrow: ${nextrow}, fileLength: ${this.fileLength})`);
                break;
            }
        }

        if (stepNumber >= maxSteps && !importRes.hasError) {
            console.warn(`[SPP Base Import] Reached maximum steps (${maxSteps}), but no error - treating as complete`);
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
