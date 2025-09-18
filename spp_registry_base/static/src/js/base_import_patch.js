/** @odoo-module **/

import {BaseImportModel} from "@base_import/import_model";

const originalExecuteImport = BaseImportModel.prototype.executeImport;

BaseImportModel.prototype.executeImport = async function (isTest = false, totalSteps, importProgress) {
    const result = await originalExecuteImport.call(this, isTest, totalSteps, importProgress);

    // Replace "Resume" warning with a custom warning for test imports
    if (isTest && result.res && result.res.nextrow) {
        // Remove the default resume warning message
        this.importMessages = this.importMessages.filter(
            (msg) => !(msg.type === "warning" && msg.lines.some((line) => line.includes("Resume")))
        );

        // Add a custom warning with the number of records tested
        const testedCount = result.res.ids.length;
        this._addMessage("info", [`Completed test import of ${testedCount} records. No data was imported.`]);
        result.res.nextrow = false; // Prevent further "Resume" prompts
        console.log(result);
        this.setOption("skip", 0);
    }

    return result;
};
