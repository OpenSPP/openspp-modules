odoo.define("spp_import_match.import", function (require) {
    var rpc = require("web.rpc");
    var DataImport = require("base_import.import").DataImport;

    DataImport.include({
        events: _.extend({}, DataImport.prototype.events, {
            "change input.oe_import_match": "_onImportMatchChanges",
        }),

        init: function () {
            this._super.apply(this, arguments);
            this.importMatchIds = [];
        },

        import_options: function () {
            var options = this._super.apply(this, arguments);
            options.use_queue = this.$("input.oe_import_queue").prop("checked");
            options.import_match_ids = this.importMatchIds;
            return options;
        },

        onimported: function () {
            if (this.$("input.oe_import_queue").prop("checked")) {
                this.displayNotification({
                    title: "Your request is being processed",
                    message: "You can check the status of this job in menu 'Queue / Jobs'.",
                    type: "success",
                });
                this.exit();
            } else {
                this._super.apply(this, arguments);
            }
        },

        exit: function () {
            this.trigger_up("history_back");
        },

        start: function () {
            var sup = this._super.apply(this, arguments);
            this.setup_import_match_selection();
            return sup;
        },

        setup_import_match_selection: function () {
            var self = this;

            rpc.query({
                model: "spp.import.match",
                method: "search_read",
                args: [[["model_id.model", "=", this.res_model]]],
                fields: ["id", "name"],
            }).then(function (data) {
                if (data.length <= 0) {
                    self.$("div#oe_config_import_matching").hide();
                    return;
                }
                var content = "";
                for (const [, value] of Object.entries(data)) {
                    const id_for_label = "o_config_checkbox_import_match_" + value.id;
                    content += `
                        <div class="custom-control custom-checkbox">
                            <input type="checkbox" id="${id_for_label}" class="custom-control-input oe_import_match"/>
                            <label for="${id_for_label}" class="custom-control-label o_form_label">${value.name}</label>
                        </div>`;
                }
                self.$("div#oe_import_match").html(content);
            });
        },

        _onImportMatchChanges: function (ev) {
            const targetIdSplited = ev.target.id.split("_");
            const importMatchId = parseInt(targetIdSplited[targetIdSplited.length - 1], 10);
            const importMatchIdIndex = this.importMatchIds.indexOf(importMatchId);
            if (importMatchIdIndex === -1) {
                this.importMatchIds.push(importMatchId);
            } else {
                this.importMatchIds.splice(importMatchIdIndex, 1);
            }
        },
    });
});
