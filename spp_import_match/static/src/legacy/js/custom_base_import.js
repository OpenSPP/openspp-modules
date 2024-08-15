/** @odoo-module */
import {BaseImportModel} from "@base_import/import_model";
import {patch} from "@web/core/utils/patch";
import {_t} from "@web/core/l10n/translation";

patch(BaseImportModel.prototype, {
    setup() {
        super.setup();
    },

    async _callImport(dryrun, args) {
        try {
            const res = await this.orm.silent.call("base_import.import", "execute_import", args, {
                dryrun,
                context: {
                    ...this.context,
                    tracking_disable: this.importOptions.tracking_disable,
                },
            });
            if ("async" in res) {
                if (res.async === true) {
                    this.displayNotification(_t("Successfully added on Queue"));
                    history.go(-1);
                }
            }
            console.log(res);
            return res;
        } catch (error) {
            // This pattern isn't optimal but it is need to have
            // similar behaviours as in legacy. That is, catching
            // all import errors and showing them inside the top
            // "messages" area.
            return {error};
        }
    },

    displayNotification(message) {
        this.env.services.action.doAction({
            type: "ir.actions.client",
            tag: "display_notification",
            params: {
                title: "Queued",
                message: message,
                type: "success",
                sticky: false,
            },
        });
    },
});
