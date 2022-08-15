odoo.define("spp_pos.CustomModels", function (require) {
    "use strict";
    // Var screens = require('point_of_sale.screens');
    var models = require("point_of_sale.models");

    models.load_fields("product.product", ["is_locked"]);
});
