/** @odoo-module **/

import {DynamicList} from "@web/model/relational_model/dynamic_list";
import {patch} from "@web/core/utils/patch";
import {_t} from "@web/core/l10n/translation";

/**
 * Patch for Odoo 17 bug: swapped parameters in archive notification message.
 *
 * Bug location: addons/web/static/src/model/relational_model/dynamic_list.js
 * GitHub: https://github.com/odoo/odoo/blob/17.0/addons/web/static/src/model/relational_model/dynamic_list.js
 *
 * Original bug shows: "Of the 20,000 records selected, only the first 50,000 have been archived"
 * Fixed to show: "Of the 50,000 records selected, only the first 20,000 have been archived"
 */

patch(DynamicList.prototype, {
    async _toggleArchive(isSelected, state) {
        const method = state ? "action_archive" : "action_unarchive";
        const context = this.context;
        const resIds = await this.getResIds(isSelected);
        const action = await this.model.orm.call(this.resModel, method, [resIds], {context});

        // FIXED: Swapped parameters from (resIds.length, this.count) to (this.count, resIds.length)
        if (
            this.isDomainSelected &&
            resIds.length === this.model.activeIdsLimit &&
            resIds.length < this.count
        ) {
            const msg = _t(
                "Of the %s records selected, only the first %s have been archived/unarchived.",
                this.count, // FIXED: Total records selected (larger number)
                resIds.length // FIXED: Actually processed (smaller number, limited)
            );
            this.model.notification.add(msg, {title: _t("Warning")});
        }

        const reload = () => this.model.load();
        if (action && Object.keys(action).length) {
            this.model.action.doAction(action, {
                onClose: reload,
            });
        } else {
            return reload();
        }
    },
});
