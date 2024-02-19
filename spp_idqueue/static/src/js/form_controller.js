/** @odoo-module **/

import {FormController} from "@web/views/form/form_controller";
import {session} from "@web/session";

class FormControllerExtend extends FormController {
    willStart() {
        const sup = this._super(...arguments);
        const acl = session.user_has_group("spp_idqueue.group_g2p_id_requestor").then((hasGroup) => {
            if (this.modelName === "res.partner" && hasGroup) {
                this.hasActionMenus = false;
            }
        });
        return Promise.all([sup, acl]);
    }
}

FormController.willStart = FormControllerExtend.willStart;
