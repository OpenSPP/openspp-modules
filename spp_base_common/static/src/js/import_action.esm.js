/** @odoo-module **/
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

import {patch} from "@web/core/utils/patch";
import {ImportAction} from "@base_import/import_action";

patch(ImportAction.prototype, {
    /**
     * Override totalSteps getter to ensure proper calculation including remainder.
     *
     * Uses Math.ceil to properly handle remainder batches:
     * - 40100 / 2000 = 20.05 → ceil(20.05) = 21 ✓
     * - 40000 / 2000 = 20.0 → ceil(20.0) = 20 ✓
     * - 100 / 2000 = 0.05 → ceil(0.05) = 1 ✓
     *
     * Previous implementations using Math.floor() + 1 incorrectly added
     * an extra step even when there was no remainder.
     */
    get totalSteps() {
        if (!this.isBatched) {
            return 1;
        }

        const totalToImport = this.totalToImport || 0;
        const batchSize = this.importOptions.limit || 2000;
        const skip = this.importOptions.skip || 0;

        if (batchSize <= 0 || totalToImport <= 0) {
            return 1;
        }

        // Calculate total including skipped records (for resume scenarios)
        const totalRecords = totalToImport + skip;
        
        // Use Math.ceil to properly include remainder in step count
        const totalSteps = Math.ceil(totalRecords / batchSize);

        console.log(
            `[SPP Base Import] Batch calculation - ` +
                `Total records: ${totalRecords} (${totalToImport} remaining + ${skip} skipped), ` +
                `Batch size: ${batchSize}, ` +
                `Total steps: ${totalSteps}`
        );

        return totalSteps;
    },
});
