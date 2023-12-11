odoo.define("spp_pos.EntitlementPopup", function (require) {
    const AbstractAwaitablePopup = require("point_of_sale.AbstractAwaitablePopup");
    const Registries = require("point_of_sale.Registries");

    var rpc = require("web.rpc");
    var entitlementid = 0;
    rpc.query({
        model: "pos.category",
        method: "get_entitlement_categ",
    }).then(function (data) {
        entitlementid = data;
    });

    class EntitlementPopup extends AbstractAwaitablePopup {
        // eslint-disable-next-line
        constructor() {
            super(...arguments);
        }

        async get_entitlement() {
            var qr_code = $("#qr_code").val();
            console.log("Search was clicked. Search for: " + qr_code);
            var productid = this.env.pos.db.get_product_by_category(entitlementid);
            var order = this.env.pos.get_order();
            if (!order) {
                order = this.env.pos.add_new_order();
            }
            rpc.query({
                model: "g2p.entitlement",
                method: "get_entitlement_code",
                args: [
                    {
                        code: qr_code,
                    },
                ],
            }).then(function (data) {
                if (data.status === "QR Doesn't Exist") {
                    console.log("Returned: " + data.status);
                    alert(data.status); // eslint-disable-line
                } else {
                    console.log("Entitlement Amount: " + data.amount);
                    console.log("Trying to Add Product with Entitlement:" + data.code);
                    console.log(productid[0]);
                    const product = productid[0];
                    const total_price = data.amount * -1;
                    const description = data.code;

                    console.log(description);
                    // Add the product after having the extra information.
                    order.add_product(product, {
                        price: total_price,
                        description: description,
                    });
                    alert("Entitlement Added!"); // eslint-disable-line
                }
            });
        }
    }
    // Create entitlement popup
    EntitlementPopup.template = "EntitlementPopup";
    EntitlementPopup.defaultProps = {
        confirmText: "Ok",
        cancelText: "Cancel",
        title: "Select Entitlements",
        body: "",
    };
    Registries.Component.add(EntitlementPopup);
    return EntitlementPopup;
});
