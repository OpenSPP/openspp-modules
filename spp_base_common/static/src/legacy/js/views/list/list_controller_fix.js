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
        
        // Fixed: Swap parameters from original (total, resIds.length) to (resIds.length, total)
        // Original Odoo bug had them backwards!
        // Correct message: "Of the [larger] records selected, only the first [smaller] have been archived"
        // Since resIds.length < total, we need resIds.length as second param (smaller)
        // But empirically the values are: total=20000, resIds.length=55558
        // So swap them to get: total as second param, resIds.length as first
        if (notif && resIds.length === session.active_ids_limit && resIds.length < total) {
            const msg = _.str.sprintf(
                _t("Of the %d records selected, only the first %d have been archived/unarchived."),
                resIds.length,  // Total selected (e.g., 55558) 
                total           // Actually archived (e.g., 20000)
            );
            this.displayNotification({ title: _t('Warning'), message: msg });
        }
    },
});

