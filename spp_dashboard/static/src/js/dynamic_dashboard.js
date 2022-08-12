odoo.define("spp_dashboard.Dashboard", function (require) {
    "use strict";

    var odoo_dynamic_dashboard = require("odoo_dynamic_dashboard.Dashboard");
    var ajax = require("web.ajax");
    var rpc = require("web.rpc");
    var ctx = {};

    odoo_dynamic_dashboard.include({
        init: function (parent, context) {
            ctx = context;
            //console.log('Context: '+ctx);
            if (ctx["context"]["active_id"]) {
                this.active_id = ctx["context"]["active_id"];
            } else {
                this.active_id = false;
            }
            this._super(parent, context);
        },

        fetch_data: function () {
            var self = this;
            //console.log('Context2: ' +ctx.id);
            var def1 = this._rpc({
                model: "dashboard.block",
                method: "get_dashboard_vals",
                args: [[], this.action_id, this.active_id],
            }).then(function (result) {
                self.block_ids = result;
            });
            return $.when(def1);
        },

        _onClick_tile: function (e) {
            e.stopPropagation();
            var self = this;
            var id = $(e.currentTarget).attr("data-id");
            ajax.jsonRpc("/tile/details", "call", {
                id: id,
                active_id: this.active_id,
            }).then(function (result) {
                self.do_action({
                    name: result["model_name"],
                    type: "ir.actions.act_window",
                    res_model: result["model"],
                    view_mode: "tree,form",
                    views: [
                        [false, "list"],
                        [false, "form"],
                    ],
                    domain: result["filter"],
                });
            });
        },
    });
});
