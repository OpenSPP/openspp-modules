odoo.define("spp_scan_id_document.field", function (require) {
    const initialise_url = "http://localhost:12212/initialise";
    const readdocument_url = "http://localhost:12212/readdocument";
    const shutdown_url = "http://localhost:12212/shutdown";

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
                }).then((initialise_response) => {
                    if (initialise_response.ok) {
                        fetch(readdocument_url, {
                            method: "GET",
                        })
                            .then((read_response) => read_response.text())
                            .then((response) => {
                                if (response === "{}") {
                                    this.onclick_started = false;
                                } else {
                                    this._setValue(response, "UPDATE");
                                    fetch(shutdown_url, {
                                        method: "GET",
                                    }).then(() => {
                                        // Shutdown completed
                                        this.onclick_started = false;
                                    });
                                }
                            });
                    } else {
                        this.onclick_started = false;
                    }
                });
            }
        },
    });

    field_registry.add("id_document_reader", DocumentReader);
});
