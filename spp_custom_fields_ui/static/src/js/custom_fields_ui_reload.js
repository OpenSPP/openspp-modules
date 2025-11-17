/** @odoo-module **/

import {FormController} from "@web/views/form/form_controller";
import {patch} from "@web/core/utils/patch";

patch(FormController.prototype, {
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

        // Try to save
        try {
            const result = await super.saveButtonClicked(params);

            // Only reload if save was successful
            // If result is defined and not false, save was successful
            if (result !== false) {
                // Reload the page to refresh the model registry
                // The URL will contain the record ID (for both new and existing records)
                window.location.reload();
            }

            return result;
        } catch (error) {
            // Save failed (validation error, required fields missing, etc.)
            // Don't reload, let the user fix the errors
            throw error;
        }
    },
});
