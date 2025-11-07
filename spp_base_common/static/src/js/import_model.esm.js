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

        console.log(`[SPP Base Import] Starting import - isTest: ${isTest}, totalSteps: ${totalSteps}, startRow: ${startRow}`);

        for (let i = 1; i <= totalSteps; i++) {
            if (this.handleInterruption) {
                console.log(`[SPP Base Import] Import interrupted at step ${i}`);
                if (importRes.hasError || isTest) {
                    importRes.nextrow = startRow;
                    this.setOption("skip", startRow);
                }
                break;
            }

            console.log(`[SPP Base Import] Executing step ${i} of ${totalSteps}`);
            const error = await this._executeImportStep(isTest, importRes);
            
            if (error) {
                console.error(`[SPP Base Import] Error at step ${i}:`, error);
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

            // Log nextrow after each step
            console.log(`[SPP Base Import] Step ${i} completed. Next row: ${importRes.nextrow || 'complete'}`);

            if (importProgress) {
                importProgress.step = i;
                importProgress.value = Math.round((100 * (i - 1)) / totalSteps);
            }
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
