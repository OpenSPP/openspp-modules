odoo.define("spp_import_match.import", function (require) {
    var rpc = require("web.rpc");
    var DataImport = require("base_import.import").DataImport;

    function _make_option(term) {
        return {id: term, text: term};
    }

    function _from_data(data, term) {
        return _.findWhere(data, {id: term}) || _make_option(term);
    }

    DataImport.include({
        import_options: function () {
            var options = this._super.apply(this, arguments);
            options.use_queue = this.$("input.oe_import_queue").prop("checked");
            return options;
        },

        onimported: function () {
            if (this.$("input.oe_import_queue").prop("checked")) {
                console.log("CHECKED QUEUE");
                this.displayNotification({
                    title: "Your request is being processed",
                    message: "You can check the status of this job in menu 'Queue / Jobs'.",
                    type: "success",
                });
                this.exit();
                console.log("CHECKED QUEUE");
            } else {
                this._super.apply(this, arguments);
            }
        },

        exit: function () {
            this.trigger_up("history_back");
        },

        start: function () {
            var sup = this._super.apply(this, arguments);
            console.log(this.res_model);
            this.setup_import_match_selection();
            return sup;
        },

        setup_import_match_selection: function () {
            var configs = [];
            var dataconfig = "_(configs)";
            var self = this;

            rpc.query({
                model: "spp.import.match",
                method: "search_read",
                args: [[["model_id.model", "=", this.res_model]]],
            }).then(function (data) {
                for (const [, value] of Object.entries(data)) {
                    configs.push(value.name);
                }
                dataconfig = _(configs);

                const res = dataconfig.map(_make_option);
                self.$("input.oe_import_match").select2({
                    width: "100%",
                    data: res,
                    // Query: dataFilteredQuery,
                    minimumResultsForSearch: -1,
                    initSelection: function ($e, c) {
                        c(_from_data(res, $e.val()) || _make_option($e.val()));
                    },
                });
            });
        },
    });
});
