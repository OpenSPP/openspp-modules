/** @odoo-module */
import {AbstractAwaitablePopup} from "@point_of_sale/app/popup/abstract_awaitable_popup";
import {_t} from "@web/core/l10n/translation";
import {usePos} from "@point_of_sale/app/store/pos_hook";
import {useService} from "@web/core/utils/hooks";
import {useState} from "@odoo/owl";

export class EntitlementPopup extends AbstractAwaitablePopup {
    setup() {
        super.setup();
        this.state = useState({inputValue: this.props.startingValue});
        this.orm = useService("orm");
        this.pos = usePos();
    }

    async getEntitlement() {
        var qr_code = $("#qr_code").val();

        const result_id = await this.orm.call("product.template", "get_entitlement_product");

        const product = this.pos.db.get_product_by_id(result_id);

        var order = this.pos.get_order();
        if (!order) {
            order = this.pos.add_new_order();
        }

        const qr_code_result = await this.orm.call("g2p.entitlement", "get_entitlement_code", [
            {code: qr_code},
        ]);
        if (qr_code_result.status === "QR Doesn't Exist") {
            console.log("Returned: " + qr_code_result.status);
            alert(qr_code_result.status);
        } else {
            const total_price = qr_code_result.amount * -1;
            const description = qr_code_result.code;
            order.add_product(product, {
                price: total_price,
                description: description,
            });
        }
    }
}

EntitlementPopup.template = "spp_pos.EntitlementPopup";
EntitlementPopup.props = {
    title: String,
    searchText: String,
    closeText: String,
    qrCodeText: String,
    entitlementCodeText: String,
};
EntitlementPopup.defaultProps = {
    title: _t("Select Entitlement"),
    searchText: _t("Search"),
    closeText: _t("Close"),
    qrCodeText: _t("Scan Entitlement QR Code"),
    entitlementCodeText: _t("Enter Entitlement Code Manually"),
};
