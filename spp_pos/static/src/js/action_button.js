/** @odoo-module **/

import {Component} from "@odoo/owl";
import {EntitlementPopup} from "./popup_voucher";
import {ProductScreen} from "@point_of_sale/app/screens/product_screen/product_screen";
import {_t} from "@web/core/l10n/translation";
import {usePos} from "@point_of_sale/app/store/pos_hook";
import {useService} from "@web/core/utils/hooks";

export class EntitlementButton extends Component {
    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
    }
    async onClickEntitlementButton() {
        this.popup.add(EntitlementPopup, {
            startingValue: "qwer",
            title: _t("Select Entitlement"),
        });
    }
}

EntitlementButton.template = "spp_pos.EntitlementButton";

ProductScreen.addControlButton({
    component: EntitlementButton,
});
