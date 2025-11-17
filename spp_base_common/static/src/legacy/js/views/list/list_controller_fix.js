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
import {patch} from "@web/core/utils/patch";

const _t = core._t;

patch(ListController.prototype, {
    /**
     * @override
     */
    async _toggleArchiveState(archive) {
        const resIds = await this.getSelectedIdsWithDomain();
        const notif = this.isDomainSelected;
        await this._archive(resIds, archive);
        const total = this.model.get(this.handle, {raw: true}).count;
        
        // Fixed: Swapped parameters from original (total, resIds.length) to (resIds.length, total)
        // Logic: resIds.length < total, so resIds.length is the smaller number (actually archived)
        //        and total is the larger number (total selected)
        if (notif && resIds.length === session.active_ids_limit && resIds.length < total) {
            const msg = _.str.sprintf(
                _t("Of the %d records selected, only the first %d have been archived/unarchived."),
                resIds.length,  // Fixed: total selected (smaller due to active_ids_limit)
                total           // Fixed: actually archived (larger - all that were selected)
            );
            this.displayNotification({ title: _t('Warning'), message: msg });
        }
    },
});

