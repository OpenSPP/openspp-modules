odoo.define("spp_scan_id_document.field", function (require) {
    const initialise_url = "http://localhost:12222/initialise";
    const readdocument_url = "http://localhost:12222/readdocument";
    const shutdown_url = "http://localhost:12222/shutdown";

    var field_registry = require("web.field_registry");

    var AbstractField = require("web.AbstractField");

    var DocumentReader = AbstractField.extend({
        template: "id_document_reader",
        xmlDependencies: ["/spp_scan_id_document/static/src/xml/registrant_widget.xml"],
        events: {
            click: "_onClick",
        },
        init: function () {
            this._super.apply(this, arguments);
            this.onclick_started = false;
        },
        _onClick: function () {
            if (!this.onclick_started) {
                this.onclick_started = true;
                fetch(initialise_url, {
                    method: "GET",
                }).then(() => {
                    fetch(readdocument_url, {
                        method: "GET",
                    })
                        .then((read_response) => read_response.text())
                        .then((response) => {
                            this._setValue(response, "UPDATE");
                            fetch(shutdown_url, {
                                method: "GET",
                            }).then(() => {
                                // Shutdown completed
                                this.onclick_started = false;
                            });
                        });
                });
            }
        },
    });

    field_registry.add("id_document_reader", DocumentReader);
});
