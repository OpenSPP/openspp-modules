odoo.define("spp_pos.EntitlementButton", function (require) {
    const {Gui} = require("point_of_sale.Gui");
    const PosComponent = require("point_of_sale.PosComponent");
    const Registries = require("point_of_sale.Registries");
    const ProductScreen = require("point_of_sale.ProductScreen");
    class OrderLineEntitlement extends PosComponent {
        display_popup_entitlement() {
            var core = require("web.core");
            var _t = core._t;
            Gui.showPopup("EntitlementPopup", {
                title: _t("Select Entitlement"),
                confirmText: _t("Close"),
                searchText: _t("Search"),
            });
        }
    }

    ProductScreen.addControlButton({
        component: OrderLineEntitlement,
        condition: function () {
            return this.env.pos;
        },
    });
    Registries.Component.add(OrderLineEntitlement);
    return OrderLineEntitlement;
});
