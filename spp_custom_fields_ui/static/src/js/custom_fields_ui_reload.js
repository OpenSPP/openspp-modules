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

        // Check if this is a new record (before save)
        const isNewRecord = !this.model.root.resId;

        // Try to save
        try {
            const result = await super.saveButtonClicked(params);

            // Only reload if save was successful
            if (result !== false) {
                if (isNewRecord) {
                    // For new records, wait a bit for URL to update, then reload
                    // This ensures the URL contains the new record ID
                    setTimeout(() => {
                        window.location.reload();
                    }, 100);
                } else {
                    // For existing records, reload immediately
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
