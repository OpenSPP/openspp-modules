/** @odoo-module **/

import {FormController} from "@web/views/form/form_controller";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";

patch(FormController.prototype, {
    setup() {
        super.setup();
        this.actionService = useService("action");
    },

    /**
     * Override the saveButtonClicked method to trigger a reload after saving
     * custom fields (ir.model.fields records with target_type).
     */
    async saveButtonClicked(params = {}) {
        // Check if we're editing ir.model.fields with target_type (custom fields UI)
        const isCustomField = this.props.resModel === "ir.model.fields" && this.model.root.data.target_type;

        if (!isCustomField) {
            return super.saveButtonClicked(params);
        }

        // Store record ID before save (will be false for new records)
        const recordIdBeforeSave = this.model.root.resId;

        // Try to save
        try {
            const result = await super.saveButtonClicked(params);

            // Only reload if save was successful
            // If result is defined and not false, save was successful
            if (result !== false) {
                const recordIdAfterSave = this.model.root.resId;

                if (!recordIdBeforeSave && recordIdAfterSave) {
                    // New record was created - reload and navigate to the saved record
                    // Use actionService to reload the current action with the new record ID
                    this.actionService.doAction({
                        type: "ir.actions.act_window",
                        res_model: this.props.resModel,
                        res_id: recordIdAfterSave,
                        views: [[false, "form"]],
                        target: "current",
                    });
                } else if (recordIdBeforeSave) {
                    // Existing record was edited - just reload the page
                    window.location.reload();
                }
            }

            return result;
        } catch (error) {
            // Save failed (validation error, required fields missing, etc.)
            // Don't reload, let the user fix the errors
            throw error;
        }
    },
});
