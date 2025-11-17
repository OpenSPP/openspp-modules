/** @odoo-module **/

/**
 * Patch for Odoo: The archive notification is generated in the model layer.
 * 
 * Reference: https://github.com/odoo/odoo/blob/17.0/addons/web/static/src/views/list/list_controller.js
 * 
 * The modern ListController just calls model.root.archive(), so we need to look elsewhere for the notification.
 * This test will verify if we can patch the controller at all.
 */

import {ListController} from "@web/views/list/list_controller";
import {patch} from "@web/core/utils/patch";

patch(ListController.prototype, {
    /**
     * @override - Test if patch works
     */
    async toggleArchiveState(archive) {
        console.log("🎯 OPENSPP PATCH IS BEING CALLED!");
        this.notification.add("🎯 OpenSPP Patch Working!", {type: "success"});
        
        // Call the original method
        if (archive) {
            return this.model.root.archive(true);
        }
        return this.model.root.unarchive(true);
    },
});

