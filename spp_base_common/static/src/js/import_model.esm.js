/** @odoo-module */
/**
 * Part of OpenSPP. See LICENSE file for full copyright and licensing details.
 *
 * Override base_import to fix batch import remainder issue in the frontend.
 *
 * For TEST imports (dryrun), we process ALL records in one go to ensure
 * the remainder is included in the test. For ACTUAL imports, we use proper
 * batch calculation with Math.ceil to include remainders.
 */

import {BaseImportModel} from "@base_import/import_model";
import {patch} from "@web/core/utils/patch";

patch(BaseImportModel.prototype, {
    /**
     * Override executeImport to handle test vs actual import differently.
     */
    async executeImport(isTest = false, totalSteps, importProgress) {
        if (isTest) {
            // For test imports, force single step to test ALL records at once
            console.log("[SPP Base Import] Test mode - processing all records in one step");
            return super.executeImport(isTest, 1, importProgress);
        } else {
            // For actual imports, use corrected totalSteps calculation
            const correctedSteps = this.totalSteps;
            console.log(`[SPP Base Import] Import mode - processing ${correctedSteps} steps`);
            return super.executeImport(isTest, correctedSteps, importProgress);
        }
    },

    /**
     * Override get totalSteps to ensure proper calculation including remainder.
     *
     * Uses Math.ceil to properly handle remainder batches:
     * - 40100 / 2000 = 20.05 → ceil(20.05) = 21 ✓
     * - 40000 / 2000 = 20.0 → ceil(20.0) = 20 ✓
     * - 100 / 2000 = 0.05 → ceil(0.05) = 1 ✓
     */
    get totalSteps() {
        const limit = this.importOptions.limit || 2000;
        
        if (!this.fileLength || limit <= 0) {
            return 1;
        }

        // Calculate total steps based on total file length
        const totalSteps = Math.ceil(this.fileLength / limit);

        console.log(
            `[SPP Base Import] Batch calculation - ` +
                `Total file records: ${this.fileLength}, ` +
                `Batch size: ${limit}, ` +
                `Total steps: ${totalSteps}`
        );

        return totalSteps;
    },
});
