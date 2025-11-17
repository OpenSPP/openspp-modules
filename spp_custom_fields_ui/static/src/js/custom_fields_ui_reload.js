/** @odoo-module **/

import {FormController} from "@web/views/form/form_controller";
import {patch} from "@web/core/utils/patch";

patch(FormController.prototype, {
    /**
     * Override the saveButtonClicked method to trigger a reload after saving
     * custom fields (ir.model.fields records with target_type).
     */
    async saveButtonClicked(params = {}) {
        const result = await super.saveButtonClicked(params);

        // Check if we're editing ir.model.fields with target_type (custom fields UI)
        if (this.props.resModel === "ir.model.fields" && this.model.root.data.target_type) {
            // Reload the page to refresh the model registry
            window.location.reload();
        }

        return result;
    },
});
