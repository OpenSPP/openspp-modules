/** @odoo-module **/

import {BaseImportModel} from "@base_import/import_model";

BaseImportModel.prototype.executeImport = async function (isTest = false, totalSteps, importProgress) {
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

    // We need to get the total number of records to import to calculate the last batch size.
    // The most reliable way is to derive it from the totalSteps and batchSize passed by the ImportAction component.
    const totalToImport =
        (totalSteps - 1) * this.importOptions.limit +
        (this.importOptions.file_length % this.importOptions.limit || this.importOptions.limit);
    console.log("Total to import:", totalToImport);
    const batchSize = this.importOptions.limit || 2000;

    for (let i = 1; i <= totalSteps + 1; i++) {
        if (this.handleInterruption) {
            if (importRes.hasError || isTest) {
                importRes.nextrow = startRow;
                this.setOption("skip", startRow);
            }
            break;
        }

        // Calculate the correct limit for each step.
        // This is the key change to ensure the last step processes the remainder.
        if (i === totalSteps && totalToImport % batchSize !== 0) {
            // Last step: process the remainder of records.
            this.importOptionsValues.limit.value = totalToImport % batchSize;
        } else {
            // For all other steps, use the full batch size.
            this.importOptionsValues.limit.value = batchSize;
        }

        const error = await this._executeImportStep(isTest, importRes);
        if (error) {
            const errorData = error.data || {};
            const message =
                (errorData.arguments && (errorData.arguments[1] || errorData.arguments[0])) ||
                "An unknown issue occurred during import. Please retry or try to split the file.";

            // Restore original batch size on error
            this.importOptionsValues.limit.value = batchSize;

            if (error.message) {
                this._addMessage("danger", [error.message, message]);
            } else {
                this._addMessage("danger", [message]);
            }

            importRes.hasError = true;
            break;
        }

        if (importProgress) {
            importProgress.step = i;
            // Update progress value based on the number of records processed so far
            const processedCount = Math.min(i * batchSize, totalToImport);
            importProgress.value = Math.round((100 * processedCount) / totalToImport);
        }
        console.log(`Completed step ${i}/${totalSteps}`);
        console.log("Next row to process:", importRes.nextrow);
        if (i === totalSteps) {
            console.log("Final step completed.");
            importRes.nextrow = startRow;
            this.setOption("skip", 0);
        }
    }
    console.log("Next row!:", importRes.nextrow);
    // Restore original batch size after completion
    this.importOptionsValues.limit.value = batchSize;

    if (!importRes.hasError) {
        if (importRes.nextrow) {
            this._addMessage("warning", [
                `Click 'Resume' to proceed with the import, resuming at line ${importRes.nextrow + 1}.`,
                "You can test or reload your file before resuming the import.",
            ]);
        }
        if (isTest) {
            this._addMessage("info", ["Everything seems valid."]);
        }
    } else {
        importRes.nextrow = startRow;
    }
    console.log("Import result:", importRes);
    return {res: importRes};
};
