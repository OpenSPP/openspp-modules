/** @odoo-module */

import {EntitlementPopup} from "@spp_pos/js/popup_voucher";
import {HaitiProductsWidget} from "@spp_pos_haiti/js/product_list";
import {patch} from "@web/core/utils/patch";

patch(EntitlementPopup.prototype, {
    setup() {
        super.setup();
        let order = this.pos.get_order();
        if (!order) {
            order = this.pos.add_new_order();
        }
        if (order.partner) {
            this.partner = order.partner;
        }
    },
});

EntitlementPopup.template = "spp_pos_haiti.EntitlementPopup";
EntitlementPopup.components = {HaitiProductsWidget};
