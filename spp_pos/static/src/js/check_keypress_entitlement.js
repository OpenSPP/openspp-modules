odoo.define("spp_pos.KeyPressEntitlement", function (require) {
    "use strict";

    const {patch} = require("web.utils");

    const KeyPressCheck = {
        ProductScreen: require("point_of_sale.ProductScreen"),
    };

    patch(KeyPressCheck.ProductScreen.prototype, "spp_pos.KeyPressEntitlement", {
        async _updateSelectedOrderline(event) {
            const _super = this._super.bind(this);
            // Await Promise.resolve();

            const selectedProduct = this.env.pos.get_order().get_selected_orderline().get_product();
            console.log("DEBUG: " + selectedProduct.is_locked);
            if (selectedProduct.is_locked == true) {
                this.playSound("error");
            } else {
                await _super(...arguments);
            }
        },
    });
    console.log(KeyPressCheck.ProductScreen.prototype);
});
