/** @odoo-module **/

/**
 * Patch for Odoo bug: swapped parameters in archive notification message.
 * 
 * Bug location: odoo/addons/web/static/src/legacy/js/views/list/list_controller.js:658-659
 * Reference: https://github.com/odoo/odoo/tree/17.0/odoo/addons/base
 * 
 * Original shows: "Of the 20,000 records selected, only the first 50,000 have been archived"
 * Fixed to show: "Of the 50,000 records selected, only the first 20,000 have been archived"
 */

import {ListController} from "@web/views/list/list_controller";
import {patch} from "@web/core/utils/patch";

patch(ListController.prototype, {
    /**
     * @override
     */
    async toggleArchiveState(archive) {
        const resIds = await this.getSelectedResIds();
        const total = this.model.root.count;
        
        await this.model.root.archive(resIds, archive);
        
        if (this.model.root.isDomainSelected && resIds.length < total) {
            const message = _.str.sprintf(
                this.env._t("Of the %d records selected, only the first %d have been archived/unarchived."),
                total,          // Fixed: swapped - total selected (larger)
                resIds.length   // Fixed: swapped - actually processed (smaller)
            );
            this.notification.add(message, { type: "warning" });
        }
    },
});

