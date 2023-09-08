odoo.define('spp_import_match.import', function (require) {
"use strict";
    var AbstractAction = require('web.AbstractAction');
    var config = require('web.config');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var session = require('web.session');
    var time = require('web.time');
    var fieldUtils = require('web.field_utils');
    var rpc = require('web.rpc');
    var DataImport = require("base_import.import").DataImport;

    function _make_option(term) { return {id: term, text: term }; }

    function _from_data(data, term) {
        return _.findWhere(data, {id: term}) || _make_option(term);
    }

    function dataFilteredQuery(q) {
    var suggestions = _.clone(this.data);
    if (q.term) {
        var exact = _.filter(suggestions, function (s) {
            return s.id === q.term || s.text === q.term;
        });
        if (exact.length) {
            suggestions = exact;
        } else {
            suggestions = [_make_option(q.term)].concat(_.filter(suggestions, function (s) {
                return s.id.indexOf(q.term) !== -1 || s.text.indexOf(q.term) !== -1
            }));
        }
    }
    q.callback({results: suggestions});
    }

    DataImport.include({

        import_options: function () {
            var options = this._super.apply(this, arguments);
            options.use_queue = this.$("input.oe_import_queue").prop("checked");
            return options;
        },

        onimported: function () {
            if (this.$("input.oe_import_queue").prop("checked")) {
                this.displayNotification({
                    type: "warning",
                    title: _t("Your request is being processed"),
                    message: _t(
                        "You can check the status of this job in menu 'Queue / Jobs'."
                    ),
                });
                this.exit();
            } else {
                this._super.apply(this, arguments);
            }
        },

        start: function () {
            var sup = this._super.apply(this, arguments);
            console.log(this.res_model);
            this.setup_import_match_selection();
            return sup;
        },

        setup_import_match_selection: function () {
            console.log(this.res_model);
            var configs = [];
            var dataconfig = "_(configs)";
            var self = this;

            rpc.query({
                model: 'ir.model',
                method: 'search_read',
                args: [[['model', '=', this.res_model]]]
            }, ).then(function (data) {
                if (data){
                    console.log("THIS 1 " + this);
                    console.log(data[0].id);
                    var model_id = data[0].id;
                    rpc.query({
                        model: 'spp.import.match',
                        method: 'search_read',
                        args: [[['model_id', '=', model_id]]]
                    }).then(function (data) {
                        console.log("THIS 2 " + this);
                        console.log(data);

                        for (const [key, value] of Object.entries(data)){
                            console.log(value.name);
                            configs.push(value.name);
                        }
                        console.log(configs);
                        dataconfig = _(configs)

                        console.log("DATA " + dataconfig);
                        var data = dataconfig.map(_make_option);
                        self.$('input.oe_import_match').select2({
                            width: '100%',
                            data: data,
                            //query: dataFilteredQuery,
                            minimumResultsForSearch: -1,
                            initSelection: function ($e, c) {
                                c(_from_data(data, $e.val()) || _make_option($e.val()))
                            },
                        });

                    });

                };
            });
        },
    });

});
