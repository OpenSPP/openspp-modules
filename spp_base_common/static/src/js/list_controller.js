odoo.define('spp_base_common.ListController', ['web.ListController', 'web.core', 'web.session'], function (require) {
"use strict";

/**
 * Fix for swapped notification message parameters when archiving/unarchiving records.
 * 
 * Original bug: Shows "Of the 20,000 records selected, only the first 50,000 have been archived"
 * This is illogical - you can't archive more records than selected.
 * 
 * Fixed to show: "Of the 50,000 records selected, only the first 20,000 have been archived"
 * This makes sense - you selected 50,000 but only 20,000 were processed due to active_ids_limit.
 * 
 * Reference: https://github.com/odoo/odoo/tree/17.0/odoo/addons/base
 */

var ListController = require('web.ListController');
var core = require('web.core');
var session = require('web.session');

var _t = core._t;

ListController.include({
    /**
     * Toggle the archive state of the selected records.
     * 
     * @override
     * @param {boolean} archive - whether to archive or unarchive
     * @returns {Promise}
     */
    _toggleArchiveState: async function (archive) {
        const resIds = await this.getSelectedIdsWithDomain();
        const notif = this.isDomainSelected;
        await this._archive(resIds, archive);
        const total = this.model.get(this.handle, {raw: true}).count;
        
        // Fixed: Swapped parameters from (total, resIds.length) to (resIds.length, total)
        // Original Odoo bug at web/static/src/legacy/js/views/list/list_controller.js:658-659
        if (notif && resIds.length === session.active_ids_limit && resIds.length < total) {
            const msg = _.str.sprintf(
                _t("Of the %d records selected, only the first %d have been archived/unarchived."),
                total,          // Fixed: total records selected (larger number)
                resIds.length   // Fixed: number actually archived/unarchived (smaller number)
            );
            this.displayNotification({ title: _t('Warning'), message: msg });
        }
    },
});

});

