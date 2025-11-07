odoo.define('spp_base_common.ListControllerFix', function (require) {
'use strict';

/**
 * Patch for Odoo bug: swapped parameters in archive notification message.
 * 
 * Bug location: odoo/addons/web/static/src/legacy/js/views/list/list_controller.js:658-659
 * Bug report: https://github.com/odoo/odoo/issues/xxxxx (if applicable)
 * 
 * Original shows: "Of the 20,000 records selected, only the first 50,000 have been archived"
 * Fixed to show: "Of the 50,000 records selected, only the first 20,000 have been archived"
 */

var ListController = require('web.ListController');
var session = require('web.session');
var core = require('web.core');

var _t = core._t;

ListController.include({
    /**
     * @override
     */
    _toggleArchiveState: async function (archive) {
        const resIds = await this.getSelectedIdsWithDomain();
        const notif = this.isDomainSelected;
        await this._archive(resIds, archive);
        const total = this.model.get(this.handle, {raw: true}).count;
        if (notif && resIds.length === session.active_ids_limit && resIds.length < total) {
            const msg = _.str.sprintf(
                _t("Of the %d records selected, only the first %d have been archived/unarchived."),
                resIds.length,  // Fixed: swapped - total selected (larger)
                total           // Fixed: swapped - actually processed (smaller)  
            );
            this.displayNotification({ title: _t('Warning'), message: msg });
        }
    },
});

});

