/** @odoo-module **/

import {FormController} from "@web/views/form/form_controller";
import {patch} from "@web/core/utils/patch";

patch(FormController.prototype, {
    /**
     * Override the saveButtonClicked method to trigger a reload after saving
     * custom fields (ir.model.fields records with target_type).
     */
    async saveButtonClicked(params = {}) {
        // Check if we're editing through the custom fields UI specifically:
        // 1. Model is ir.model.fields
        // 2. Has target_type (grp or indv)
        // 3. Model is res.partner (the target of custom fields)
        // 4. State is manual (not base fields)
        // 5. Context has default_model = 'res.partner' (from the custom fields UI actions)
        const isCustomFieldUI =
            this.props.resModel === "ir.model.fields" &&
            this.model.root.data.target_type &&
            this.model.root.data.model === "res.partner" &&
            this.model.root.data.state === "manual" &&
            this.props.context?.default_model === "res.partner";

        if (!isCustomFieldUI) {
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
