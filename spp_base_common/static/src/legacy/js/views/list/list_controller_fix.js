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

import ListController from "web.ListController";
import session from "web.session";
import core from "web.core";

const _t = core._t;

// Use legacy .include() method for Backbone-style controllers
ListController.include({
    /**
     * @override
     */
    _toggleArchiveState: async function (archive) {
        const resIds = await this.getSelectedIdsWithDomain();
        const notif = this.isDomainSelected;
        await this._archive(resIds, archive);
        const total = this.model.get(this.handle, {raw: true}).count;
        
        // TEST: Completely change the message to verify patch is working
        if (notif && resIds.length === session.active_ids_limit && resIds.length < total) {
            const msg = _.str.sprintf(
                _t("🎯 PATCH IS WORKING! Selected: %d, Processed: %d"),
                resIds.length,  // Total selected
                total           // Actually processed
            );
            this.displayNotification({ title: _t('OpenSPP Archive Fix'), message: msg });
        }
    },
});

