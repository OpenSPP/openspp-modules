/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

// Patch for Odoo bug: swapped parameters in archive notification
patch(ListController.prototype, {
    async _toggleArchive(isSelected, state) {
        const method = state ? "action_archive" : "action_unarchive";
        const context = this.context;
        const resIds = await this.getResIds(isSelected);
        const action = await this.model.orm.call(this.resModel, method, [resIds], {
            context
        });
        
        // FIXED: Swapped this.count and resIds.length
        if (this.isDomainSelected && resIds.length === this.model.activeIdsLimit && resIds.length < this.count) {
            const msg = _t(
                "Of the %s records selected, only the first %s have been archived/unarchived.", 
                this.count,      // FIXED: Total records selected (larger)
                resIds.length    // FIXED: Actually processed (smaller)
            );
            this.model.notification.add(msg, {
                title: _t("Warning")
            });
        }
        
        const reload = () => this.model.load();
        if (action && Object.keys(action).length) {
            this.model.action.doAction(action, {
                onClose: reload,
            });
        } else {
            return reload();
        }
    }
});

