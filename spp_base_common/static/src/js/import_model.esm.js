/** @odoo-module */
/**
 * Part of OpenSPP. See LICENSE file for full copyright and licensing details.
 *
 * Override base_import to fix batch import remainder issue in the frontend.
 *
 * The goal is to ensure that when calculating total steps for batch imports,
 * the remainder is included properly. For example, 40100 records with batch
 * size 2000 should create 21 steps (20 batches of 2000 + 1 batch of 100),
 * not 20 or 22 steps.
 */

import {BaseImportModel} from "@base_import/import_model";
import {patch} from "@web/core/utils/patch";

patch(BaseImportModel.prototype, {
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
        const skip = this.importOptions.skip || 0;
        
        if (!this.fileLength || limit <= 0) {
            return 1;
        }

        // Calculate total steps including any skipped rows (for resume)
        const totalRecords = this.fileLength;
        const totalSteps = Math.ceil(totalRecords / limit);

        console.log(
            `[SPP Base Import] Batch calculation - ` +
                `Total file records: ${totalRecords}, ` +
                `Skip: ${skip}, ` +
                `Batch size: ${limit}, ` +
                `Total steps: ${totalSteps}`
        );

        return totalSteps;
    },
});

