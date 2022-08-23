odoo.define("g2p_programs.create_program_button", function (require) {
    "use strict";
    var core = require("web.core");
    var ListController = require("web.ListController");
    var rpc = require("web.rpc");
    var session = require("web.session");
    var _t = core._t;
    ListController.include({
        renderButtons: function () {
            this._super.apply(this, arguments);
            if (this.$buttons) {
                this.$buttons.find(".o_list_button_add_program").click(this.proxy("load_wizard"));
            }
        },

        load_wizard: function () {
            var self = this;
            self.do_action({
                name: "Set Program Settings",
                type: "ir.actions.act_window",
                res_model: "g2p.program.create.wizard",
                views: [[false, "form"]],
                view_mode: "form",
                target: "new",
            });
            return window.location;
        },

        load_wizard2: function () {
            var self = this;
            var user = session.uid;
            rpc.query({
                model: "g2p.program",
                method: "get_values",
                args: [[user], {id: user}],
            }).then(function () {
                self.do_action({
                    name: _t("action_invoices"),
                    type: "ir.actions.act_window",
                    res_model: "name.name",
                    views: [[false, "form"]],
                    view_mode: "form",
                    target: "new",
                });
                return window.location;
            });
        },
    });
});
